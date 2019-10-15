from queue import Queue
from threading import Thread

from ipykernel.kernelbase import Kernel
import re
import subprocess
import tempfile
import os
import os.path as path


class RealTimeSubprocess(subprocess.Popen):
    """
    A subprocess that allows to read its stdout and stderr in real time
    """

    def __init__(self, cmd, write_to_stdout, write_to_stderr):
        """
        :param cmd: the command to execute
        :param write_to_stdout: a callable that will be called with chunks of data from stdout
        :param write_to_stderr: a callable that will be called with chunks of data from stderr
        """
        self._write_to_stdout = write_to_stdout
        self._write_to_stderr = write_to_stderr

        super().__init__(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)

        self._stdout_queue = Queue()
        self._stdout_thread = Thread(target=RealTimeSubprocess._enqueue_output, args=(self.stdout, self._stdout_queue))
        self._stdout_thread.daemon = True
        self._stdout_thread.start()

        self._stderr_queue = Queue()
        self._stderr_thread = Thread(target=RealTimeSubprocess._enqueue_output, args=(self.stderr, self._stderr_queue))
        self._stderr_thread.daemon = True
        self._stderr_thread.start()

    @staticmethod
    def _enqueue_output(stream, queue):
        """
        Add chunks of data from a stream to a queue until the stream is empty.
        """
        for line in iter(lambda: stream.read(4096), b''):
            queue.put(line)
        stream.close()

    def write_contents(self):
        """
        Write the available content from stdin and stderr where specified when the instance was created
        :return:
        """

        def read_all_from_queue(queue):
            res = b''
            size = queue.qsize()
            while size != 0:
                res += queue.get_nowait()
                size -= 1
            return res

        stdout_contents = read_all_from_queue(self._stdout_queue)
        if stdout_contents:
            self._write_to_stdout(stdout_contents)
        stderr_contents = read_all_from_queue(self._stderr_queue)
        if stderr_contents:
            self._write_to_stderr(stderr_contents)


class GwionKernel(Kernel):
    implementation = 'jupyter_gwion_kernel'
    implementation_version = '0.1'
    language = 'gwion'
    language_version = 'N/A'
    language_info = {'name': 'gwion',
                     'mimetype': 'text/plain',
                     'file_extension': '.gw'}
    banner = "Gwion kernel.\n" \
             "creates source code files in temporary folder.\n"

    def __init__(self, *args, **kwargs):
        super(GwionKernel, self).__init__(*args, **kwargs)
        self.files = []
        filepath = path.dirname(path.realpath(__file__))
        subprocess.call(['gwion', filepath])

    def cleanup_files(self):
        """Remove all the temporary files created by the kernel"""
        for file in self.files:
            os.remove(file)

    def new_temp_file(self, **kwargs):
        """Create a new temp file to be deleted when the kernel shuts down"""
        # We don't want the file to be deleted when closed, but only when the kernel stops
        kwargs['delete'] = False
        kwargs['mode'] = 'w'
        file = tempfile.NamedTemporaryFile(**kwargs)
        self.files.append(file.name)
        return file

    def _write_to_stdout(self, contents):
        self.send_response(self.iopub_socket, 'stream', {'name': 'stdout', 'text': contents})

    def _write_to_stderr(self, contents):
        self.send_response(self.iopub_socket, 'stream', {'name': 'stderr', 'text': contents})

    def create_jupyter_subprocess(self, cmd):
        return RealTimeSubprocess(cmd,
                                  lambda contents: self._write_to_stdout(contents.decode()),
                                  lambda contents: self._write_to_stderr(contents.decode()))

    def compile_with_gwion(self, source_filename, gwargs=None, fileargs=None):
        gwargs = gwargs
        filename = source_filename
        for flag in fileargs:
           filename += ":" + flag
        args = ['gwion', filename] + gwargs
        return self.create_jupyter_subprocess(args)

    def _filter_magics(self, code):

        magics = {'gwargs': [],
                  'fileargs': []}

        for line in code.splitlines():
            if line.startswith('#!%'):
                key, value = line[3:].split(":", 2)
                key = key.strip().lower()
                if key == "gwargs":
                    for flag in value.split():
                        magics[key] += [flag]
                elif key == "fileargs":
                    # Split arguments respecting quotes
                    for argument in re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', value):
                        magics['fileargs'] += [argument.strip('"')]

        return magics

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):

        magics = self._filter_magics(code)

        with self.new_temp_file(suffix='.gw') as source_file:
            source_file.write(code)
            source_file.flush()
            p = self.compile_with_gwion(source_file.name, magics['gwargs'], magics['fileargs'])
            while p.poll() is None:
              p.write_contents()
            p.write_contents()
            if p.returncode != 0:  # Compilation failed
              self._write_to_stderr("[Gwion kernel] Gwion exited with code {}".format(
                                    p.returncode))
              return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [],
                          'user_expressions': {}}
        while p.poll() is None:
            p.write_contents()
        p.write_contents()

        if p.returncode != 0:
            self._write_to_stderr("[Gwion kernel] Executable exited with code {}".format(p.returncode))
        return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [], 'user_expressions': {}}

    def do_shutdown(self, restart):
        """Cleanup the created source code files and executables when shutting down the kernel"""
        self.cleanup_files()

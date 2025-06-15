# Kimera SWM System Update Report

**Update Date:** Sun Jun 15 16:40:54 2025
**Duration:** 138.60 seconds
**Status:** completed

## Updates Applied

- [SUCCESS] Dependencies Updated
- [SUCCESS] Embedding Model Updated
- [SUCCESS] Database Optimized
- [SUCCESS] Vault System Optimized
- [SUCCESS] Monitoring System Updated
- [SUCCESS] System Tests Completed
- [SUCCESS] System Cleanup Completed

## Performance Improvements

- [STARTING] Embedding model stats: {'total_embeddings': 1, 'total_time': 0.30834245681762695, 'avg_time_per_embedding': 0.30834245681762695, 'model_load_time': 10.771526575088501}
- [STARTING] Database optimization completed
- [STARTING] Vault rebalancing: moved 0 scars
- [STARTING] Monitoring system active with 4 metrics
- [STARTING] [WARNING] API health check skipped: HTTPConnectionPool(host='localhost', port=8000): Max retries exceeded with url: /system/status (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002BC0C3E1E80>: Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it'))
- [STARTING] [SUCCESS] Embedding system test passed
- [STARTING] [SUCCESS] Database connection test passed
- [STARTING] Cleaned up 12 temporary items

## Errors Encountered

- [FAILED] Unknown: error: subprocess-exited-with-error
  
  Getting requirements to build wheel did not run successfully.
  exit code: 1
  
  [48 lines of output]
  Traceback (most recent call last):
    File "C:\Users\Loomine\AppData\Local\Programs\Python\Python313\Lib\site-packages\pip\_vendor\pyproject_hooks\_in_process\_in_process.py", line 389, in <module>
      main()
      ~~~~^^
    File "C:\Users\Loomine\AppData\Local\Programs\Python\Python313\Lib\site-packages\pip\_vendor\pyproject_hooks\_in_process\_in_process.py", line 373, in main
      json_out["return_val"] = hook(**hook_input["kwargs"])
                               ~~~~^^^^^^^^^^^^^^^^^^^^^^^^
    File "C:\Users\Loomine\AppData\Local\Programs\Python\Python313\Lib\site-packages\pip\_vendor\pyproject_hooks\_in_process\_in_process.py", line 143, in get_requires_for_build_wheel
      return hook(config_settings)
    File "C:\Users\Loomine\AppData\Local\Temp\pip-build-env-mya63w37\overlay\Lib\site-packages\setuptools\build_meta.py", line 331, in get_requires_for_build_wheel
      return self._get_build_requires(config_settings, requirements=[])
             ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "C:\Users\Loomine\AppData\Local\Temp\pip-build-env-mya63w37\overlay\Lib\site-packages\setuptools\build_meta.py", line 301, in _get_build_requires
      self.run_setup()
      ~~~~~~~~~~~~~~^^
    File "C:\Users\Loomine\AppData\Local\Temp\pip-build-env-mya63w37\overlay\Lib\site-packages\setuptools\build_meta.py", line 512, in run_setup
      super().run_setup(setup_script=setup_script)
      ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "C:\Users\Loomine\AppData\Local\Temp\pip-build-env-mya63w37\overlay\Lib\site-packages\setuptools\build_meta.py", line 317, in run_setup
      exec(code, locals())
      ~~~~^^^^^^^^^^^^^^^^
    File "<string>", line 128, in <module>
    File "C:\Users\Loomine\AppData\Local\Programs\Python\Python313\Lib\subprocess.py", line 414, in check_call
      retcode = call(*popenargs, **kwargs)
    File "C:\Users\Loomine\AppData\Local\Programs\Python\Python313\Lib\subprocess.py", line 395, in call
      with Popen(*popenargs, **kwargs) as p:
           ~~~~~^^^^^^^^^^^^^^^^^^^^^^
    File "C:\Users\Loomine\AppData\Local\Programs\Python\Python313\Lib\subprocess.py", line 1039, in __init__
      self._execute_child(args, executable, preexec_fn, close_fds,
      ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                          pass_fds, cwd, env,
                          ^^^^^^^^^^^^^^^^^^^
      ...<5 lines>...
                          gid, gids, uid, umask,
                          ^^^^^^^^^^^^^^^^^^^^^^
                          start_new_session, process_group)
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "C:\Users\Loomine\AppData\Local\Programs\Python\Python313\Lib\subprocess.py", line 1551, in _execute_child
      hp, ht, pid, tid = _winapi.CreateProcess(executable, args,
                         ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^
                               # no special security
                               ^^^^^^^^^^^^^^^^^^^^^
      ...<4 lines>...
                               cwd,
                               ^^^^
                               startupinfo)
                               ^^^^^^^^^^^^
  FileNotFoundError: [WinError 2] The system cannot find the file specified
  [end of output]
  
  note: This error originates from a subprocess, and is likely not a problem with pip.
error: subprocess-exited-with-error

Getting requirements to build wheel did not run successfully.
exit code: 1

See above for output.

note: This error originates from a subprocess, and is likely not a problem with pip.
- [FAILED] Unknown: error: subprocess-exited-with-error
  
  Getting requirements to build wheel did not run successfully.
  exit code: 1
  
  [48 lines of output]
  Traceback (most recent call last):
    File "C:\Users\Loomine\AppData\Local\Programs\Python\Python313\Lib\site-packages\pip\_vendor\pyproject_hooks\_in_process\_in_process.py", line 389, in <module>
      main()
      ~~~~^^
    File "C:\Users\Loomine\AppData\Local\Programs\Python\Python313\Lib\site-packages\pip\_vendor\pyproject_hooks\_in_process\_in_process.py", line 373, in main
      json_out["return_val"] = hook(**hook_input["kwargs"])
                               ~~~~^^^^^^^^^^^^^^^^^^^^^^^^
    File "C:\Users\Loomine\AppData\Local\Programs\Python\Python313\Lib\site-packages\pip\_vendor\pyproject_hooks\_in_process\_in_process.py", line 143, in get_requires_for_build_wheel
      return hook(config_settings)
    File "C:\Users\Loomine\AppData\Local\Temp\pip-build-env-1f_f4aum\overlay\Lib\site-packages\setuptools\build_meta.py", line 331, in get_requires_for_build_wheel
      return self._get_build_requires(config_settings, requirements=[])
             ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "C:\Users\Loomine\AppData\Local\Temp\pip-build-env-1f_f4aum\overlay\Lib\site-packages\setuptools\build_meta.py", line 301, in _get_build_requires
      self.run_setup()
      ~~~~~~~~~~~~~~^^
    File "C:\Users\Loomine\AppData\Local\Temp\pip-build-env-1f_f4aum\overlay\Lib\site-packages\setuptools\build_meta.py", line 512, in run_setup
      super().run_setup(setup_script=setup_script)
      ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "C:\Users\Loomine\AppData\Local\Temp\pip-build-env-1f_f4aum\overlay\Lib\site-packages\setuptools\build_meta.py", line 317, in run_setup
      exec(code, locals())
      ~~~~^^^^^^^^^^^^^^^^
    File "<string>", line 128, in <module>
    File "C:\Users\Loomine\AppData\Local\Programs\Python\Python313\Lib\subprocess.py", line 414, in check_call
      retcode = call(*popenargs, **kwargs)
    File "C:\Users\Loomine\AppData\Local\Programs\Python\Python313\Lib\subprocess.py", line 395, in call
      with Popen(*popenargs, **kwargs) as p:
           ~~~~~^^^^^^^^^^^^^^^^^^^^^^
    File "C:\Users\Loomine\AppData\Local\Programs\Python\Python313\Lib\subprocess.py", line 1039, in __init__
      self._execute_child(args, executable, preexec_fn, close_fds,
      ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                          pass_fds, cwd, env,
                          ^^^^^^^^^^^^^^^^^^^
      ...<5 lines>...
                          gid, gids, uid, umask,
                          ^^^^^^^^^^^^^^^^^^^^^^
                          start_new_session, process_group)
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "C:\Users\Loomine\AppData\Local\Programs\Python\Python313\Lib\subprocess.py", line 1551, in _execute_child
      hp, ht, pid, tid = _winapi.CreateProcess(executable, args,
                         ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^
                               # no special security
                               ^^^^^^^^^^^^^^^^^^^^^
      ...<4 lines>...
                               cwd,
                               ^^^^
                               startupinfo)
                               ^^^^^^^^^^^^
  FileNotFoundError: [WinError 2] The system cannot find the file specified
  [end of output]
  
  note: This error originates from a subprocess, and is likely not a problem with pip.
error: subprocess-exited-with-error

Getting requirements to build wheel did not run successfully.
exit code: 1

See above for output.

note: This error originates from a subprocess, and is likely not a problem with pip.

## Summary

Successfully applied 7 updates with 8 performance improvements and 2 errors.

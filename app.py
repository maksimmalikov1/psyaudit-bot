 mod = importlib.import_module(module)
  File "/opt/render/project/python/Python-3.14.3/lib/python3.14/importlib/__init__.py", line 88, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1398, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1371, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1342, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 938, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 755, in exec_module
  File "<frozen importlib._bootstrap_external>", line 893, in get_code
  File "<frozen importlib._bootstrap_external>", line 823, in source_to_code
  File "<frozen importlib._bootstrap>", line 491, in _call_with_frames_removed
  File "/opt/render/project/src/app.py", line 62
    return jsonify({"error": "invalid signature"}), 403
    ^^^^^^
IndentationError: expected an indented block after 'if' statement on line 61
==> Exited with status 1
==> Common ways to troubleshoot your deploy: https://render.com/docs/troubleshooting-deploys
==> Running 'gunicorn app:app'
Traceback (most recent call last):
  File "/opt/render/project/src/.venv/bin/gunicorn", line 7, in <module>
    sys.exit(run())
             ~~~^^
  File "/opt/render/project/src/.venv/lib/python3.14/site-packages/gunicorn/app/wsgiapp.py", line 66, in run
    WSGIApplication("%(prog)s [OPTIONS] [APP_MODULE]", prog=prog).run()
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.14/site-packages/gunicorn/app/base.py", line 235, in run
    super().run()
    ~~~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.14/site-packages/gunicorn/app/base.py", line 71, in run
    Arbiter(self).run()
    ~~~~~~~^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.14/site-packages/gunicorn/arbiter.py", line 63, in __init__
    self.setup(app)
    ~~~~~~~~~~^^^^^
  File "/opt/render/project/src/.venv/lib/python3.14/site-packages/gunicorn/arbiter.py", line 139, in setup
    self.app.wsgi()
    ~~~~~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.14/site-packages/gunicorn/app/base.py", line 66, in wsgi
    self.callable = self.load()
                    ~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.14/site-packages/gunicorn/app/wsgiapp.py", line 57, in load
    return self.load_wsgiapp()
           ~~~~~~~~~~~~~~~~~^^
  File "/opt/render/project/src/.venv/lib/python3.14/site-packages/gunicorn/app/wsgiapp.py", line 47, in load_wsgiapp
    return util.import_app(self.app_uri)
           ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^
  File "/opt/render/project/src/.venv/lib/python3.14/site-packages/gunicorn/util.py", line 411, in import_app
    mod = importlib.import_module(module)
  File "/opt/render/project/python/Python-3.14.3/lib/python3.14/importlib/__init__.py", line 88, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1398, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1371, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1342, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 938, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 755, in exec_module
  File "<frozen importlib._bootstrap_external>", line 893, in get_code
  File "<frozen importlib._bootstrap_external>", line 823, in source_to_code
  File "<frozen importlib._bootstrap>", line 491, in _call_with_frames_removed
  File "/opt/render/project/src/app.py", line 62
    return jsonify({"error": "invalid signature"}), 403
    ^^^^^^
IndentationError: expected an indented block after 'if' statement on line 61
127.0.0.1 - - [23/May/2026:22:03:05 +0000] "POST /webhook HTTP/1.1" 403 30 "-" "curl"
127.0.0.1 - - [23/May/2026:22:03:18 +0000] "POST /tg HTTP/1.1" 200 12 "-" "-"
127.0.0.1 - - [23/May/2026:22:04:21 +0000] "POST /webhook HTTP/1.1" 403 30 "-" "curl"
127.0.0.1 - - [23/May/2026:22:05:04 +0000] "POST /webhook HTTP/1.1" 403 30 "-" "curl"
127.0.0.1 - - [23/May/2026:22:05:05 +0000] "POST /webhook HTTP/1.1" 403 30 "-" "curl"
127.0.0.1 - - [23/May/2026:22:06:05 +0000] "POST /webhook HTTP/1.1" 403 30 "-" "curl"
==> Deploying...
==> Setting WEB_CONCURRENCY=1 by default, based on available CPUs in the instance
==> Running 'gunicorn app:app'
[2026-05-23 22:06:40 +0000] [59] [INFO] Starting gunicorn 26.0.0
[2026-05-23 22:06:40 +0000] [59] [INFO] Listening at: http://0.0.0.0:10000 (59)
[2026-05-23 22:06:40 +0000] [59] [INFO] Using worker: sync
[2026-05-23 22:06:40 +0000] [60] [INFO] Booting worker with pid: 60
127.0.0.1 - - [23/May/2026:22:06:41 +0000] "HEAD / HTTP/1.1" 404 0 "-" "Go-http-client/1.1"
[2026-05-23 22:06:41 +0000] [59] [INFO] Control socket listening at /opt/render/.gunicorn/gunicorn.ctl
==> Your service is live 🎉
==> 
==> ///////////////////////////////////////////////////////////
==> 
==> Available at your primary URL https://psyaudit-bot.onrender.com
==> 
==> ///////////////////////////////////////////////////////////
127.0.0.1 - - [23/May/2026:22:06:51 +0000] "GET / HTTP/1.1" 404 207 "-" "Go-http-client/2.0"
127.0.0.1 - - [23/May/2026:22:07:07 +0000] "POST /webhook HTTP/1.1" 400 27 "-" "curl"
127.0.0.1 - - [23/May/2026:22:07:47 +0000] "POST /tg HTTP/1.1" 200 12 "-" "-"
[2026-05-23 22:07:50 +0000] [58] [INFO] Handling signal: term
[2026-05-23 22:07:50 +0000] [59] [INFO] Worker exiting (pid: 59)
[2026-05-23 22:07:51 +0000] [58] [INFO] Shutting down: Master
127.0.0.1 - - [23/May/2026:22:08:05 +0000] "POST /webhook HTTP/1.1" 400 27 "-" "curl"
127.0.0.1 - - [23/May/2026:22:09:21 +0000] "POST /webhook HTTP/1.1" 400 27 "-" "curl"
127.0.0.1 - - [23/May/2026:22:09:22 +0000] "POST /webhook HTTP/1.1" 400 27 "-" "curl"
127.0.0.1 - - [23/May/2026:22:10:05 +0000] "POST /webhook HTTP/1.1" 400 27 "-" "curl"
127.0.0.1 - - [23/May/2026:22:11:04 +0000] "POST /webhook HTTP/1.1" 400 27 "-" "curl"
127.0.0.1 - - [23/May/2026:22:11:04 +0000] "POST /webhook HTTP/1.1" 400 27 "-" "curl"
==> Detected service running on port 10000

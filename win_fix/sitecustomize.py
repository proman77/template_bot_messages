import asyncio
import sys
import os

if sys.platform == "win32":
    try:
        from asyncio import windows_events
        import selectors
        
        # Force the policy
        selector_policy = windows_events.WindowsSelectorEventLoopPolicy()
        asyncio.set_event_loop_policy(selector_policy)
        
        # Monkeypatch set_event_loop_policy
        _old_set_policy = asyncio.set_event_loop_policy
        def _new_set_policy(policy):
            # print(f"DEBUG: [PID {os.getpid()}] set_event_loop_policy called with {type(policy)}", file=sys.stderr)
            if isinstance(policy, windows_events.WindowsProactorEventLoopPolicy):
                return
            _old_set_policy(policy)
        asyncio.set_event_loop_policy = _new_set_policy
        
        # Overwrite the Proactor policy class
        windows_events.WindowsProactorEventLoopPolicy = windows_events.WindowsSelectorEventLoopPolicy
        windows_events.DefaultEventLoopPolicy = windows_events.WindowsSelectorEventLoopPolicy
        
        # Monkeypatch new_event_loop
        _old_new_loop = asyncio.new_event_loop
        def _new_event_loop_fixed():
            # print(f"DEBUG: [PID {os.getpid()}] new_event_loop called", file=sys.stderr)
            return asyncio.SelectorEventLoop()
        asyncio.new_event_loop = _new_event_loop_fixed
        
        # Monkeypatch get_event_loop to ensure it returns a SelectorEventLoop
        _old_get_loop = asyncio.get_event_loop
        def _get_event_loop_fixed():
            try:
                loop = _old_get_loop()
                if isinstance(loop, windows_events.ProactorEventLoop):
                    # print(f"DEBUG: [PID {os.getpid()}] get_event_loop returned Proactor, replacing...", file=sys.stderr)
                    new_loop = asyncio.SelectorEventLoop()
                    asyncio.set_event_loop(new_loop)
                    return new_loop
                return loop
            except RuntimeError:
                new_loop = asyncio.SelectorEventLoop()
                asyncio.set_event_loop(new_loop)
                return new_loop
        asyncio.get_event_loop = _get_event_loop_fixed

        # print(f"DEBUG: [PID {os.getpid()}] sitecustomize.py applied SelectorEventLoop fix", file=sys.stderr)
    except Exception:
        pass

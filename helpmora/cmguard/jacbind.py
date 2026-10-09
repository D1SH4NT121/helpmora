"""Make jac-scale listen on loopback only, behind the gateway, and mount integration routes.

1. Hooks JFastApiServer to automatically mount HELPmora's Omi, Qdrant, and Lyzr
   integration routes (/api/...).
2. Binds upstream to loopback if HELPMORA_UPSTREAM_BIND is set.
"""

import os
import sys


def bind_upstream() -> str:
    try:
        import jaclang
        from jac_scale.jserver.jfast_api import JFastApiServer
        if not getattr(JFastApiServer, "_helpmora_router_hooked", False):
            orig_create_server = JFastApiServer.create_server

            def hooked_create_server(self, *args, **kwargs):
                fastapi_app = orig_create_server(self, *args, **kwargs)
                try:
                    # Support running from either root or helpmora/ directory
                    curr_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    if curr_dir not in sys.path:
                        sys.path.insert(0, curr_dir)
                    parent_dir = os.path.dirname(curr_dir)
                    if parent_dir not in sys.path:
                        sys.path.insert(0, parent_dir)

                    try:
                        from integrations.api import router as integrations_router, root_router
                    except ImportError:
                        from helpmora.integrations.api import router as integrations_router, root_router

                    old_count = len(fastapi_app.router.routes)
                    fastapi_app.include_router(integrations_router)
                    fastapi_app.include_router(root_router)
                    new_routes = fastapi_app.router.routes[old_count:]
                    # Prepend new routes before SPA wildcard catch-all route
                    fastapi_app.router.routes = new_routes + fastapi_app.router.routes[:old_count]
                except Exception as ex:
                    print("Error mounting integrations router:", ex)
                return fastapi_app

            JFastApiServer.create_server = hooked_create_server
            JFastApiServer._helpmora_router_hooked = True
    except Exception as ex:
        print("Hook error:", ex)

    host = os.environ.get("HELPMORA_UPSTREAM_BIND", "").strip()
    if not host:
        return ""
    try:
        import jaclang
        from jac_scale.jserver.jfast_api import JFastApiServer
        run = JFastApiServer.run_server
        if getattr(run, "_helpmora_bind", False):
            return host

        def run_server(self, *args, **kwargs):
            kwargs["host"] = host
            return run(self, *args, **kwargs)

        run_server._helpmora_bind = True
        JFastApiServer.run_server = run_server
        return host
    except Exception:
        return ""

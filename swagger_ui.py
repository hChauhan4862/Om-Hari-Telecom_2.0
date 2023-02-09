from src.endpoints._base import *
from fastapi.responses import HTMLResponse
router = APIRouter(include_in_schema=False)

@router.get("/docs")
async def custom_swagger_ui_html():
    content = """<!DOCTYPE html>
<html>

<head>
    <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui.css">
    <title>Om Hari Telecom - APIs</title>
</head>

<body>
    <div id="swagger-ui">
    </div>
	<script src="https://unpkg.com/react@15/dist/react.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-bundle.js"></script>
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
        const hc = React.createElement
        const ui = SwaggerUIBundle({
            url: '/openapi.json',
            "dom_id": "#swagger-ui",
            "layout": "BaseLayout",
            "deepLinking": true,
            "showExtensions": true,
            "showCommonExtensions": true,
            "defaultModelsExpandDepth": -1,
            "persistAuthorization": true,
            oauth2RedirectUrl: window.location.origin + '/docs/oauth2-redirect',
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIBundle.SwaggerUIStandalonePreset,
                system => {
                    // Variable to capture the security prop of OperationSummary
                    // then pass it to authorizeOperationBtn
                    let currentSecurity
                    return {
                        wrapComponents: {
                            // Wrap OperationSummary component to get its prop
                            OperationSummary: Original => props => {
                                const security = props.operationProps.get('security')
                                currentSecurity = security.toJS()
                                return hc(Original, props)
                            },
                            // Wrap the padlock button to show the
                            // scopes required for current operation
                            authorizeOperationBtn: Original =>
                                function (props) {
                                    return hc('div', {}, [
                                        ...(currentSecurity || []).map(scheme => {
                                            const schemeName = Object.keys(scheme)[0]
                                            if (!scheme[schemeName].length) return null

                                            const scopes = scheme[schemeName].flatMap(scope => [
                                                hc('code', null, scope),
                                                ', ',
                                            ])
                                            scopes.pop()
                                            return hc('span', null, [schemeName, '(', ...scopes, ')'])
                                        }),
                                        hc(Original, props),
                                    ])
                                },
                        },
                    }
                },
            ]
        },
        )

    </script>
</body>

</html>"""
    return HTMLResponse(content=content)

@router.get("/docs/oauth2-redirect", )
async def custom_swagger_ui_html():
    content = """

    <!doctype html>
    <html lang="en-US">
    <head>
        <title>Swagger UI: OAuth2 Redirect</title>
    </head>
    <body>
    <script>
        'use strict';
        function run () {
            var oauth2 = window.opener.swaggerUIRedirectOauth2;
            var sentState = oauth2.state;
            var redirectUrl = oauth2.redirectUrl;
            var isValid, qp, arr;

            if (/code|token|error/.test(window.location.hash)) {
                qp = window.location.hash.substring(1).replace('?', '&');
            } else {
                qp = location.search.substring(1);
            }

            arr = qp.split("&");
            arr.forEach(function (v,i,_arr) { _arr[i] = '"' + v.replace('=', '":"') + '"';});
            qp = qp ? JSON.parse('{' + arr.join() + '}',
                    function (key, value) {
                        return key === "" ? value : decodeURIComponent(value);
                    }
            ) : {};

            isValid = qp.state === sentState;

            if ((
              oauth2.auth.schema.get("flow") === "accessCode" ||
              oauth2.auth.schema.get("flow") === "authorizationCode" ||
              oauth2.auth.schema.get("flow") === "authorization_code"
            ) && !oauth2.auth.code) {
                if (!isValid) {
                    oauth2.errCb({
                        authId: oauth2.auth.name,
                        source: "auth",
                        level: "warning",
                        message: "Authorization may be unsafe, passed state was changed in server. The passed state wasn't returned from auth server."
                    });
                }

                if (qp.code) {
                    delete oauth2.state;
                    oauth2.auth.code = qp.code;
                    oauth2.callback({auth: oauth2.auth, redirectUrl: redirectUrl});
                } else {
                    let oauthErrorMsg;
                    if (qp.error) {
                        oauthErrorMsg = "["+qp.error+"]: " +
                            (qp.error_description ? qp.error_description+ ". " : "no accessCode received from the server. ") +
                            (qp.error_uri ? "More info: "+qp.error_uri : "");
                    }

                    oauth2.errCb({
                        authId: oauth2.auth.name,
                        source: "auth",
                        level: "error",
                        message: oauthErrorMsg || "[Authorization failed]: no accessCode received from the server."
                    });
                }
            } else {
                oauth2.callback({auth: oauth2.auth, token: qp, isValid: isValid, redirectUrl: redirectUrl});
            }
            window.close();
        }

        if (document.readyState !== 'loading') {
            run();
        } else {
            document.addEventListener('DOMContentLoaded', function () {
                run();
            });
        }
    </script>
    </body>
    </html>"""
    return HTMLResponse(content=content)
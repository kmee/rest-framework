{
    "name": "FastAPI Auth Partner",
    "summary": "Autenticação de parceiros via FastAPI",
    "version": "17.0.1.0.0",
    "author": "OCA, Akretion",
    "license": "AGPL-3",
    "depends": ["base", "auth_partner", "fastapi"],
    "data": [
        "security/ir.model.access.csv",
        "security/res_group.xml",
        "views/auth_directory_view.xml",
        "views/auth_partner_view.xml",
        "views/fastapi_endpoint_view.xml",
        "wizards/wizard_auth_partner_impersonate_view.xml",
        "wizards/wizard_auth_partner_reset_password_view.xml",
        "demo/fastapi_endpoint_demo.xml"
    ],
    "installable": True,
}

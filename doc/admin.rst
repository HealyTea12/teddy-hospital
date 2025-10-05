How to for admins

=================

Configuring the application
===========================

To configure the application, you can change options in `backend/config.toml`

- `DEBUG`: is an debug option, true or false
- `CARROUSSEL_SIZE`: determines how many pictures are stored for the carousel, must be intiger > 0
- `RESULTS_PER_IMAGE`: determines how many x-rays the AI generates for each request, must be intiger > 0
- `ANIMAL_TYPES[]`: animal types that can be specified by the user when uploading, used by the AI, array of strings

Configuring storage
-------------------

The best way of configuring seafile is with the repo token. That makes sure that in case the repo token is leaked,
that nobody has access to the rest of your seafile account. To generate such a token you can either follow the GUI
via "Library context menu (the three dots next to the library name) -> Advanced -> API Token". However, teddy-hospital only works with a repo token if the seafile API is of version >= 12.

In case your Seafile is version < 12, you should use your account token. You can get it by running:

```
curl --request POST \
     --url <seafile_url>/api2/auth-token/ \
     [--header 'X-SEAFILE-OTP: <otp>'] \
     --header 'accept: application/json' \
     --header 'content-type: application/json' \
     --data '
{
  "username": <username>,
  "password": <password>
}
'
```

The 'X-SEAFILE-OTP' is the 6 digit code you get usually on your phone in case two factor authentification is activated. You can also get the account token through the GUI.

If you are really lazy and don't want to generate the tokens, you can also just put in your username and password. Only one of these authentication methods needs to be present and you can delete the ones you are not using from the `config.toml`.
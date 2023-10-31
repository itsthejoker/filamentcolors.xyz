# filamentcolors.xyz
The source code for a small website to compare pieces of printed filament.

Public API
---

Please give credit if you use my work for your project! Let me know if you do use this for something; I always love to see how this information is used!

https://filamentcolors.xyz/api/

If you use my API for a project, I politely request that you check out my patreon to help pay for server costs: https://www.patreon.com/filamentcolors. I also have a way to do one-time donations of any amount here: https://buy.stripe.com/8wMbKg8UT4k8fBKaEE

API notes:
---

- Color family is marked by a 3-letter code for data savings; the map can be found here: https://github.com/itsthejoker/filamentcolors.xyz/blob/master/filamentcolors/models.py#L165-L176
- /api/swatch/ has some sort methods available to it: `type` and `manufacturer`. See https://github.com/itsthejoker/filamentcolors.xyz/blob/master/filamentcolors/api/views.py#L36 for the source.
- Example urls:
  - https://filamentcolors.xyz/api/swatch/?m=manufacturer
  - https://filamentcolors.xyz/api/swatch/?m=type

Please don't hammer the API if you're just checking for a specific piece of information like color values; instead, please keep a cache of the information that's important to you. There's a quick endpoint that you can use to validate that the information you have cached and the server information are the same.

Send a GET request to https://filamentcolors.xyz/api/version/; you'll get the following response: `{"db_version": 1, "db_last_modified": 1586021667}`. The `db_version` will be incremented if the _schema_ changes (which for right now, assume that it is stable), and the `db_last_modified` key is an ISO timestamp of the last time there was a swatch uploaded.

If you have any questions, please feel free to reach out to me via email at [joe@filamentcolors.xyz](mailto:joe@filamentcolors.xyz)!

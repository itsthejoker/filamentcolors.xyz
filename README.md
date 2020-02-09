# filamentcolors.xyz
The source code for a small website to compare pieces of printed filament.

Public API
---

Please give credit if you use my work for your project! Let me know if you do use this for something; I always love to see how this information is used!

https://filamentcolors.xyz/api/

API notes:
---

- Color family is marked by a 3 letter code for data savings; the map can be found here: https://github.com/itsthejoker/filamentcolors.xyz/blob/master/filamentcolors/models.py#L74-L100
- /api/swatch/ has several sort methods available to it: `type`, `manufacturer`, and `color`. See https://github.com/itsthejoker/filamentcolors.xyz/blob/master/filamentcolors/api/views.py#L18 for the source.
- Example urls:
  - https://filamentcolors.xyz/api/swatch/?m=color
  - https://filamentcolors.xyz/api/swatch/?m=type

# filamentcolors.xyz
The source code for a small website to compare pieces of printed filament.

Public API
---

https://filamentcolors.xyz/api/

API notes:
---

- Color family is marked by a 3 letter code for data savings; the map can be found here: https://github.com/itsthejoker/filamentcolors.xyz/blob/master/filamentcolors/models.py#L74-L100
- /api/swatch/ has several sort methods available to it: `type`, `manufacturer`, and `color`. See https://github.com/itsthejoker/filamentcolors.xyz/blob/master/filamentcolors/api/views.py#L18 for the source.
- Example urls:
  - https://filamentcolors.xyz/api/swatch/?m=color
  - https://filamentcolors.xyz/api/swatch/?m=type

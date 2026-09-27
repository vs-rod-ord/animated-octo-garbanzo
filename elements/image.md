---
name: image
description: The image element — embedding a raster image file into the OLF, sized by aspect ratio.
metadata:
  type: element
  status: proven
  dsl_support: full
  related: [spec/dsl-spec]
---

# `image`

```yaml
- image: {src: diagram.png, at: top-right, width: 400}   # height auto from aspect ratio
```

`src` resolves relative to the spec file (or, in an MCP-tool context, relative to
whatever the tool documents as its file-resolution root — check the specific
tool's own docs if unsure, don't assume). The engine embeds the file inside the
OLF zip and wires the element reference automatically.

## Rules

- `height` is never specified — it is always derived from the image's own aspect
  ratio and the given `width`.
- This element embeds a real image file. If you don't have an actual image file
  to embed (e.g. you were only asked to describe a diagram), don't fabricate a
  `src:` path — either omit the image or ask where the file is.

## Worked `content.json`

```json
{
  "image": {
    "id": "UUID",
    "x": 100.0,
    "y": 150.0,
    "width": 640.0,
    "height": 480.0,
    "mime-type": "image/png",
    "source": "images/example.png",
    "matrix": "1,0,0,0,1,0,0,0,1"
  }
}
```

- `source` must exactly match the image file's path **inside the OLF zip**,
  conventionally under an `images/` subfolder at the zip root (alongside
  `content.json`) — the actual bytes of the image must be packaged into the
  zip at that same path when you build the archive, not just referenced.
- `mime-type` is `image/png` or `image/jpeg` — these are the only two
  confirmed-supported formats.
- **No `additional` array entry is needed for `image`** — unlike shapes and
  lines, image elements aren't referenced there.

"""Build the ZIP-level mockup: simplify real ZCTA boundaries for the 10 FTB counties and embed them
in template.html. Values shown in the page are invented; only the geography is real.

Inputs (public Census-derived GeoJSON, download once and keep OUTSIDE the repo):
  curl -o fl_zips.json https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master/fl_florida_zip_codes_geo.min.json
  curl -o counties.json https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json

Run:  python3 -I mockup/zip/build.py --geo-dir /path/to/geo
"""
import argparse
import json
import math
import os

COUNTIES = [  # name, county FIPS
    ("Citrus", "017"), ("Hardee", "049"), ("Hernando", "053"), ("Highlands", "055"),
    ("Hillsborough", "057"), ("Manatee", "081"), ("Pasco", "101"), ("Pinellas", "103"),
    ("Polk", "105"), ("Sumter", "119"),
]
FIPS_TO_IDX = {f: i for i, (_, f) in enumerate(COUNTIES)}
WIDTH = 760.0


def polys(geom):
    return [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]


def pip(x, y, ring):
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def dp(pts, tol):
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        ax, ay = pts[a]
        bx, by = pts[b]
        dx, dy = bx - ax, by - ay
        norm = math.hypot(dx, dy) or 1e-12
        best, idx = -1.0, -1
        for i in range(a + 1, b):
            d = abs(dy * (pts[i][0] - ax) - dx * (pts[i][1] - ay)) / norm
            if d > best:
                best, idx = d, i
        if best > tol:
            keep[idx] = True
            stack.extend([(a, idx), (idx, b)])
    return [p for p, k in zip(pts, keep) if k]


def simplify_ring(pts, tol):
    """Douglas-Peucker on a closed ring: split at the point farthest from the start so the chord is non-degenerate."""
    if len(pts) < 5:
        return pts
    x0, y0 = pts[0]
    far = max(range(1, len(pts) - 1), key=lambda i: (pts[i][0] - x0) ** 2 + (pts[i][1] - y0) ** 2)
    a = dp(pts[: far + 1], tol)
    b = dp(pts[far:], tol)
    return a[:-1] + b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geo-dir", required=True)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "food-need-forecast-map-zip.html"))
    args = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(args.geo_dir, "counties.json")) as f:
        cj = json.load(f)
    cfeat = {}
    for ft in cj["features"]:
        p = ft["properties"]
        if p["STATE"] == "12" and p["COUNTY"] in FIPS_TO_IDX:
            cfeat[FIPS_TO_IDX[p["COUNTY"]]] = ft["geometry"]
    assert len(cfeat) == len(COUNTIES), "missing county geometry"

    with open(os.path.join(args.geo_dir, "fl_zips.json")) as f:
        zj = json.load(f)
    zips = []
    for ft in zj["features"]:
        p = ft["properties"]
        lon, lat = float(p["INTPTLON10"]), float(p["INTPTLAT10"])
        ci = None
        for i, g in cfeat.items():
            if any(pip(lon, lat, poly[0]) for poly in polys(g)):
                ci = i
                break
        if ci is not None:
            zips.append({"z": p["ZCTA5CE10"], "ci": ci, "lon": lon, "lat": lat,
                         "a": round(p["ALAND10"] / 1e6, 2), "geom": ft["geometry"]})
    zips.sort(key=lambda z: z["z"])

    lons = [pt[0] for g in cfeat.values() for poly in polys(g) for pt in poly[0]]
    lats = [pt[1] for g in cfeat.values() for poly in polys(g) for pt in poly[0]]
    for z in zips:
        for poly in polys(z["geom"]):
            for pt in poly[0]:
                lons.append(pt[0]); lats.append(pt[1])
    lon0, lon1, lat0, lat1 = min(lons), max(lons), min(lats), max(lats)
    kx = math.cos(math.radians((lat0 + lat1) / 2))
    s = WIDTH / ((lon1 - lon0) * kx)
    proj = lambda lon, lat: ((lon - lon0) * kx * s, (lat1 - lat) * s)
    height = (lat1 - lat0) * s

    def path(geom, tol):
        out = []
        for poly in polys(geom):
            for ring in poly:
                pts = simplify_ring([proj(a, b) for a, b in ring], tol)
                if len(pts) >= 4:
                    out.append("M" + " ".join("%.1f,%.1f" % q for q in pts) + "Z")
        return "".join(out)

    zout = []
    for z in zips:
        x, y = proj(z["lon"], z["lat"])
        zout.append({"z": z["z"], "c": z["ci"], "d": path(z["geom"], 0.45), "x": round(x, 1), "y": round(y, 1), "a": z["a"]})
    cout = []
    for i, (name, _) in enumerate(COUNTIES):
        pts = [proj(a, b) for poly in polys(cfeat[i]) for a, b in poly[0]]
        xs, ys = [q[0] for q in pts], [q[1] for q in pts]
        cout.append({"n": name, "d": path(cfeat[i], 0.4), "bb": [round(min(xs), 1), round(min(ys), 1), round(max(xs), 1), round(max(ys), 1)]})

    geo = {"w": round(WIDTH, 1), "h": round(height, 1), "zips": zout, "counties": cout}
    with open(os.path.join(here, "template.html")) as f:
        html = f.read()
    html = html.replace("/*__GEO__*/", "const GEO = " + json.dumps(geo, separators=(",", ":")) + ";")
    with open(args.out, "w") as f:
        f.write(html)
    counts = {}
    for z in zips:
        counts[COUNTIES[z["ci"]][0]] = counts.get(COUNTIES[z["ci"]][0], 0) + 1
    print("ZIPs:", len(zips), counts, "html KB:", len(html) // 1024)


if __name__ == "__main__":
    main()

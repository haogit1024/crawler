var LZString = function () {
    function o(o, r) {
        if (!t[o]) {
            t[o] = {};
            for (var n = 0; n < o.length; n++) t[o][o.charAt(n)] = n
        }
        return t[o][r]
    }
    var r = String.fromCharCode,
        n = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",
        e = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-$",
        t = {},
        i = {
            compressToBase64: function (o) {
                if (null == o) return "";
                var r = i._compress(o, 6, function (o) {
                    return n.charAt(o)
                });
                switch (r.length % 4) {
                    default:
                    case 0:
                        return r;
                    case 1:
                        return r + "===";
                    case 2:
                        return r + "==";
                    case 3:
                        return r + "="
                }
            },
            decompressFromBase64: function (r) {
                return null == r ? "" : "" == r ? null : i._decompress(r.length, 32, function (e) {
                    return o(n, r.charAt(e))
                })
            },
            compressToUTF16: function (o) {
                return null == o ? "" : i._compress(o, 15, function (o) {
                    return r(o + 32)
                }) + " "
            },
            decompressFromUTF16: function (o) {
                return null == o ? "" : "" == o ? null : i._decompress(o.length, 16384, function (r) {
                    return o.charCodeAt(r) - 32
                })
            },
            compressToUint8Array: function (o) {
                for (var r = i.compress(o), n = new Uint8Array(2 * r.length), e = 0, t = r.length; t > e; e++) {
                    var s = r.charCodeAt(e);
                    n[2 * e] = s >>> 8, n[2 * e + 1] = s % 256
                }
                return n
            },
            decompressFromUint8Array: function (o) {
                if (null === o || void 0 === o) return i.decompress(o);
                for (var n = new Array(o.length / 2), e = 0, t = n.length; t > e; e++) n[e] = 256 * o[2 * e] + o[2 * e + 1];
                var s = [];
                return n.forEach(function (o) {
                    s.push(r(o))
                }), i.decompress(s.join(""))
            },
            compressToEncodedURIComponent: function (o) {
                return null == o ? "" : i._compress(o, 6, function (o) {
                    return e.charAt(o)
                })
            },
            decompressFromEncodedURIComponent: function (r) {
                return null == r ? "" : "" == r ? null : (r = r.replace(/ /g, "+"), i._decompress(r.length, 32, function (n) {
                    return o(e, r.charAt(n))
                }))
            },
            compress: function (o) {
                return i._compress(o, 16, function (o) {
                    return r(o)
                })
            },
            _compress: function (o, r, n) {
                if (null == o) return "";
                var e, t, i, s = {},
                    p = {},
                    u = "",
                    c = "",
                    a = "",
                    l = 2,
                    f = 3,
                    h = 2,
                    d = [],
                    m = 0,
                    v = 0;
                for (i = 0; i < o.length; i += 1)
                    if (u = o.charAt(i), Object.prototype.hasOwnProperty.call(s, u) || (s[u] = f++, p[u] = !0), c = a + u, Object.prototype.hasOwnProperty.call(s, c)) a = c;
                    else {
                        if (Object.prototype.hasOwnProperty.call(p, a)) {
                            if (a.charCodeAt(0) < 256) {
                                for (e = 0; h > e; e++) m <<= 1, v == r - 1 ? (v = 0, d.push(n(m)), m = 0) : v++;
                                for (t = a.charCodeAt(0), e = 0; 8 > e; e++) m = m << 1 | 1 & t, v == r - 1 ? (v = 0, d.push(n(m)), m = 0) : v++, t >>= 1
                            } else {
                                for (t = 1, e = 0; h > e; e++) m = m << 1 | t, v == r - 1 ? (v = 0, d.push(n(m)), m = 0) : v++, t = 0;
                                for (t = a.charCodeAt(0), e = 0; 16 > e; e++) m = m << 1 | 1 & t, v == r - 1 ? (v = 0, d.push(n(m)), m = 0) : v++, t >>= 1
                            }
                            l--, 0 == l && (l = Math.pow(2, h), h++), delete p[a]
                        } else
                            for (t = s[a], e = 0; h > e; e++) m = m << 1 | 1 & t, v == r - 1 ? (v = 0, d.push(n(m)), m = 0) : v++, t >>= 1;
                        l--, 0 == l && (l = Math.pow(2, h), h++), s[c] = f++, a = String(u)
                    } if ("" !== a) {
                    if (Object.prototype.hasOwnProperty.call(p, a)) {
                        if (a.charCodeAt(0) < 256) {
                            for (e = 0; h > e; e++) m <<= 1, v == r - 1 ? (v = 0, d.push(n(m)), m = 0) : v++;
                            for (t = a.charCodeAt(0), e = 0; 8 > e; e++) m = m << 1 | 1 & t, v == r - 1 ? (v = 0, d.push(n(m)), m = 0) : v++, t >>= 1
                        } else {
                            for (t = 1, e = 0; h > e; e++) m = m << 1 | t, v == r - 1 ? (v = 0, d.push(n(m)), m = 0) : v++, t = 0;
                            for (t = a.charCodeAt(0), e = 0; 16 > e; e++) m = m << 1 | 1 & t, v == r - 1 ? (v = 0, d.push(n(m)), m = 0) : v++, t >>= 1
                        }
                        l--, 0 == l && (l = Math.pow(2, h), h++), delete p[a]
                    } else
                        for (t = s[a], e = 0; h > e; e++) m = m << 1 | 1 & t, v == r - 1 ? (v = 0, d.push(n(m)), m = 0) : v++, t >>= 1;
                    l--, 0 == l && (l = Math.pow(2, h), h++)
                }
                for (t = 2, e = 0; h > e; e++) m = m << 1 | 1 & t, v == r - 1 ? (v = 0, d.push(n(m)), m = 0) : v++, t >>= 1;
                for (;;) {
                    if (m <<= 1, v == r - 1) {
                        d.push(n(m));
                        break
                    }
                    v++
                }
                return d.join("")
            },
            decompress: function (o) {
                return null == o ? "" : "" == o ? null : i._decompress(o.length, 32768, function (r) {
                    return o.charCodeAt(r)
                })
            },
            _decompress: function (o, n, e) {
                var t, i, s, p, u, c, a, l, f = [],
                    h = 4,
                    d = 4,
                    m = 3,
                    v = "",
                    w = [],
                    A = {
                        val: e(0),
                        position: n,
                        index: 1
                    };
                for (i = 0; 3 > i; i += 1) f[i] = i;
                for (p = 0, c = Math.pow(2, 2), a = 1; a != c;) u = A.val & A.position, A.position >>= 1, 0 == A.position && (A.position = n, A.val = e(A.index++)), p |= (u > 0 ? 1 : 0) * a, a <<= 1;
                switch (t = p) {
                    case 0:
                        for (p = 0, c = Math.pow(2, 8), a = 1; a != c;) u = A.val & A.position, A.position >>= 1, 0 == A.position && (A.position = n, A.val = e(A.index++)), p |= (u > 0 ? 1 : 0) * a, a <<= 1;
                        l = r(p);
                        break;
                    case 1:
                        for (p = 0, c = Math.pow(2, 16), a = 1; a != c;) u = A.val & A.position, A.position >>= 1, 0 == A.position && (A.position = n, A.val = e(A.index++)), p |= (u > 0 ? 1 : 0) * a, a <<= 1;
                        l = r(p);
                        break;
                    case 2:
                        return ""
                }
                for (f[3] = l, s = l, w.push(l);;) {
                    if (A.index > o) return "";
                    for (p = 0, c = Math.pow(2, m), a = 1; a != c;) u = A.val & A.position, A.position >>= 1, 0 == A.position && (A.position = n, A.val = e(A.index++)), p |= (u > 0 ? 1 : 0) * a, a <<= 1;
                    switch (l = p) {
                        case 0:
                            for (p = 0, c = Math.pow(2, 8), a = 1; a != c;) u = A.val & A.position, A.position >>= 1, 0 == A.position && (A.position = n, A.val = e(A.index++)), p |= (u > 0 ? 1 : 0) * a, a <<= 1;
                            f[d++] = r(p), l = d - 1, h--;
                            break;
                        case 1:
                            for (p = 0, c = Math.pow(2, 16), a = 1; a != c;) u = A.val & A.position, A.position >>= 1, 0 == A.position && (A.position = n, A.val = e(A.index++)), p |= (u > 0 ? 1 : 0) * a, a <<= 1;
                            f[d++] = r(p), l = d - 1, h--;
                            break;
                        case 2:
                            return w.join("")
                    }
                    if (0 == h && (h = Math.pow(2, m), m++), f[l]) v = f[l];
                    else {
                        if (l !== d) return null;
                        v = s + s.charAt(0)
                    }
                    w.push(v), f[d++] = s + v.charAt(0), h--, s = v, 0 == h && (h = Math.pow(2, m), m++)
                }
            }
        };
    return i
}();
"function" == typeof define && define.amd ? define(function () {
    return LZString
}) : "undefined" != typeof module && null != module && (module.exports = LZString);

// let image_data = "JYWw5g9AjATAHHA7BALFKBOGyoFYUBscGADAMy5nACOcA6gJ4BaA1hgCID6AkgEIA2AGTKIAdACsADmAA0oSLATI0mbNHxFSFCgBVJAJxCSUvAPIBjElACiZAG4ApCdLnho8JKnRYcG4uVwYFABNAAsABWAAMwBaAFdeAEV+GIBxMABBbmdZeXclL1VfQn8KKAZEnVwAYXYAIzrcEAAXADEQAAkAZQBZHNcFD2VvNTwSrVwoOgA5albJACVmyQANVODqmIBVAEMAaX68xU8VH3VxgJIo61xeTjIQfX0eznZwwQWDqVy3Y+Gi86aS7iVLAEiSTgAZ0QK0kwG44QY/Awh1+Q0KZzGQLIKAwGBW1RgdgWMXMCy2wQW02m7EkqMGBVOoz8WhQcAA7ok4ltqtYVgtJAw7K1muEwCh6fkTiNitiUIgyNNEiQAF7Wbg9awAO2o0zswAWkMlfwxzIuOMQMTskmqDA6LAyMS6vHM1EEwCN3wGUv+mJZ5EIwTAkIIADVggAPdg9XBRYAAEzAUT6XqO6KZstKhDoAFNQnAGNZEFAmCRUuz44IoMBjemZYCs7gmAxzCxmhGW5IVTBIZCUOZQ7XGfWsVmUJIWHsyD1uBh0DpWjFEKkulAh9KAaPWWRqLxeAB7LYdAgLFALFjmfS8YKCde+s1yndxEiJcL78I7fcEBxCmJMFZ3qamasjABA6FAiDVNw1BdOE4iQvw1T7tSgEZg2rJQHsoRkB0dQ9FqUDiNwHR5oksKoSO/o4lAOihlqWpMLgRb6JCMDSOwDCpBRm5USgJAgCwUCpCq8aQvGKogOwcTNNwph2NxfrmmQGDxvuGCCHQ8H8NMoQYCwrQwCsOwKQ+pTKfG7B0JC1CSIg0zxpBwBdCszRxCZwHkGQcC4Fs3laqYdDhIkGRxF0KqQj07LuehnlwNQOzAHUJg7Dm1hdKGPRRPw/LRVunmID0DDTM+cA6PuGQivGznsnUuVUWQBCSOEKq4OIgiJDEKC4Ik+6CCghh1UpBD7igUQLEwTBgM05ggF0wQZCq7I1qmaLDjxSm4FqcScLgKzcHsqRvqYEYZAO+6DdiFCJHQLALIIUSSO6wSpPodShPGDAXWZKCQlE1BkFqWx0JwOziMA7CCHOAErQyG6KZdZAkOyDiqeIEYYJy7AqiQdSJDmX1aGQZDVFAGTsDEWrWII3BRCAqR2Bg5UE55MC4PuHTVEwDjVCsoZ1PukILPGkhbMzRMwHU4hauIcT6LsXR8QwYBxHULBi2QUBkMEWrsjmS4YB01gTnsMQEME6uYR0Fl0PwYC8HEKxMNMi2OOr5DsPu4hQFEew5uI5hwPupgsPophizAGBhQQGT6FEghgAsdStIg+hQIk1jhxg/ChqGoSpJxZChB0gjhPoMTRuHcAwBkgjvWAGCpD0zSJDsuoOM0lepDmCy8EYKoZCsMRwFsWw6AQKrh4gCzBMeBDADo7IoDAoe8K05hdOH49apCvCIFsMCtCgqRbAwJDvhPMM+kBMVkKz1DxkweGmAQIBxHEIDVNMBAMGrl8mmheVb64EhK0cI7IQBbF4BGImoRwA9H0NMcOKB2A5laNJIMexBB1HCNwdgOgWDxiQdUMgYBqjUA6M0Ow+gVRwD2L5XAv8XBpjWvDUoMAyCSAcNMSQ3Aui62qAQXgdQFh8C4n/Os61sQwBgKGagJAYjxi1CgaYhAdCQh2OyOwn1xEsNMloaRdQuhdGqOIBYOhBCQjAK0XScA4hRHDiQfQewWAdAoDsKaXRpg7FwOEKIUUdFwz0eQGASMGD6A6FEAg/ACAwC2M0OghlcD4wCfeDyGs9KaKNnQCCWx2ARmCHsQG2jpBAA="
// let img_data_arr = LZString.decompressFromBase64(image_data).split(',');
// console.log(img_data_arr)
var arguments = process.argv.splice(2);  //获得入参
var image_data = arguments[0];
let img_data_arr = LZString.decompressFromBase64(image_data).split(',');
console.log(JSON.stringify(img_data_arr))

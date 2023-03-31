/*
    © 2023 Telefónica Digital España S.L.

    This file is part of XAIoGraphs.

    XAIoGraphs is free software: you can redistribute it and/or modify it under the terms of
    the Affero GNU General Public License as published by the Free Software Foundation,
    either version 3 of the License, or (at your option) any later version.

    XAIoGraphs is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
    without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    See the Affero GNU General Public License for more details.

    You should have received a copy of the Affero GNU General Public License along with XAIoGraphs.
    If not, see https://www.gnu.org/licenses/.
*/

(() => { "use strict"; var e, _ = {}, i = {}; function n(e) { var a = i[e]; if (void 0 !== a) return a.exports; var r = i[e] = { exports: {} }; return _[e].call(r.exports, r, r.exports, n), r.exports } n.m = _, e = [], n.O = (a, r, u, l) => { if (!r) { var o = 1 / 0; for (f = 0; f < e.length; f++) { for (var [r, u, l] = e[f], s = !0, t = 0; t < r.length; t++)(!1 & l || o >= l) && Object.keys(n.O).every(d => n.O[d](r[t])) ? r.splice(t--, 1) : (s = !1, l < o && (o = l)); if (s) { e.splice(f--, 1); var c = u(); void 0 !== c && (a = c) } } return a } l = l || 0; for (var f = e.length; f > 0 && e[f - 1][2] > l; f--)e[f] = e[f - 1]; e[f] = [r, u, l] }, n.n = e => { var a = e && e.__esModule ? () => e.default : () => e; return n.d(a, { a }), a }, n.d = (e, a) => { for (var r in a) n.o(a, r) && !n.o(e, r) && Object.defineProperty(e, r, { enumerable: !0, get: a[r] }) }, n.o = (e, a) => Object.prototype.hasOwnProperty.call(e, a), (() => { var e = { 666: 0 }; n.O.j = u => 0 === e[u]; var a = (u, l) => { var t, c, [f, o, s] = l, v = 0; if (f.some(b => 0 !== e[b])) { for (t in o) n.o(o, t) && (n.m[t] = o[t]); if (s) var p = s(n) } for (u && u(l); v < f.length; v++)n.o(e, c = f[v]) && e[c] && e[c][0](), e[c] = 0; return n.O(p) }, r = self.webpackChunkviz = self.webpackChunkviz || []; r.forEach(a.bind(null, 0)), r.push = a.bind(null, r.push.bind(r)) })() })();

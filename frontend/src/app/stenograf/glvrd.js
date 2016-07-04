// function DelayedFunctionWithCancel(e, t, n) {
//     function r() {
//         n(), o && clearTimeout(o);
//         var r = arguments;
//         o = setTimeout(function() {
//             e.apply(this, r)
//         }, t)
//     }
//     var o = !1;
//     return r
// }

// function DelayedFunction(e, t) {
//     function n() {
//         r && clearTimeout(r);
//         var n = arguments;
//         r = setTimeout(function() {
//             e.apply(this, n)
//         }, t)
//     }
//     var r = !1;
//     return n
// }

// function GetCaretPosition(e) {
//     var t = saveSelection(e),
//         n = 0;
//     return t && (n = t.start), n
// }

// function SetCaretPosition(e, t) {
//     var n = {};
//     n.start = t, n.end = t, restoreSelection(e, n)
// }

// function RandomChoice(e) {
//     return 0 == e.length ? null : e[RandomInt(e.length)]
// }

// function RandomInt(e) {
//     return Math.floor(Math.random() * e)
// }

// function PluralRu(e, t, n, r, o) {
//     e = Math.abs(e), e % 1 != 0 && (decimal_part = String(e).split(".")[1], e = decimal_part);
//     var a = e % 100,
//         i = e % 10,
//         s = r;
//     return s = 0 == e ? o || r : a > 10 && 20 > a ? r : 0 == i ? r : 1 == i ? t : i > 1 && 5 > i ? n : r
// }
// $.fn.glavred = function(e) {
//     function t(e) {
//         S.sort(function(e, t) {
//             return t.start - e.start
//         });
//         for (var t = 0; t < S.length; t++) {
//             var n = S[t],
//                 r = w[n.clean_text];
//             r && (r.formatted_text || (r.formatted_text = l(n.clean_text, r.ranges)), e = u(e, r.formatted_text, n.start, n.end))
//         }
//         C.setValue(e), C.restoreCaret(), H = C.getHints()
//     }

//     function n(e) {
//         var t = [];
//         for (var n in w)
//             for (var r = w[n].ranges, o = 0; o < r.length; o++) - 1 == t.indexOf(r[o][2]) && t.push(r[o][2]);
//         for (var a = [], i = 0; i < t.length; i++) "undefined" == typeof y[t[i]] && a.push(t[i]);
//         if (a.length > 0) {
//             var s = {
//                 csrfmiddlewaretoken: m.csrf_token,
//                 rules: JSON.stringify(a)
//             };
//             $.post(m.rules_url, s, function(t) {
//                 y = $.extend(y, t.rules), e && e()
//             })
//         } else e && e()
//     }

//     function r() {
//         o(), C.hasClass("processing") || (_ = !1, C.addClass("processing"), h.trigger("glavred:process", [B])), C.saveCaret();
//         var e = C.getValue();
//         S = g(e);
//         var r = f(S, w),
//             a = (r.old_chunks, r.new_chunks),
//             i = a.map(function(e) {
//                 return e.clean_text
//             });
//         if (0 == i.length) return t(e), n(), s(), c(), _ = !0, C.removeClass("processing"), void h.trigger("glavred:processed", [B, !1]);
//         var l = {
//             csrfmiddlewaretoken: m.csrf_token,
//             chunks: JSON.stringify(i)
//         };
//         x = $.post(m.process_url, l, function(r) {
//             x = null;
//             for (var o = r.chunks_ranges, i = 0; i < o.length; i++) {
//                 var l = a[i],
//                     u = o[i];
//                 w[l.clean_text] = {
//                     ranges: u
//                 }
//             }
//             t(e), n(function() {
//                 h.trigger("glavred:processed", [B, r])
//             }), H.filter('[data-rule="' + b + '"]').addClass("active"), s(), c(), _ = !0, C.removeClass("processing"), h.trigger("glavred:processed", [B, r])
//         })
//     }

//     function o() {
//         x && (x.abort(), x = null), C.removeClass("processing"), h.trigger("glavred:processed", [B, null])
//     }

//     function a(e, t) {
//         var n = 50,
//             r = C.getHeight();
//         if (r += n, t += n, y[e]) {
//             if (b != e) E.fadeOut(150, function() {
//                 var o = y[e].description;
//                 E.html(o), E.css("margin-top", n), E.fadeIn(350), setTimeout(function() {
//                     E.innerHeight() + t > r && (t = r - E.innerHeight()), n > t && (t = n), E.css("margin-top", t)
//                 }, 50)
//             });
//             else {
//                 var o = E.css("margin-top");
//                 E.css("margin-top", n), E.css("opacity", 1), E.innerHeight() + t > r && (t = r - E.innerHeight()), n > t && (t = n), E.css("margin-top", o), E.animate({
//                     "margin-top": t
//                 }, 250)
//             }
//             H.removeClass("active").removeClass("current"), H.filter('[data-rule="' + e + '"]').addClass("active"), b = e
//         }
//     }

//     function i() {
//         E.hide(), b = null
//     }

//     function s() {
//         var e = C.getCaretElement();
//         e && e.is("em") && (k = e)
//     }

//     function c() {
//         if (P) return H.removeClass("current"), H.removeClass("active"), i(), H.filter(function(e, t) {
//             return y[$(t).data("rule")].section == P ? t : null
//         }).addClass("active"), void h.trigger("glavred:activesectionchanged", [B, P]);
//         var e = R || k;
//         e ? (a(e.data("rule"), e.position().top), H.removeClass("current"), e.addClass("current"), h.trigger("glavred:activesectionchanged", [B, y[e.data("rule")].section])) : H.removeClass("current")
//     }

//     function l(e, t) {
//         t.sort(function(e, t) {
//             return t[0] - e[0]
//         });
//         for (var n = "</em>", r = 0; r < t.length; r++) {
//             var o = t[r][0],
//                 a = t[r][1],
//                 i = t[r][2],
//                 s = '<em data-rule="' + i + '">';
//             e = u(e, n, a, a), e = u(e, s, o, o)
//         }
//         return e
//     }

//     function u(e, t, n, r) {
//         return e.slice(0, n) + t + e.slice(r, e.length)
//     }

//     function g(e) {
//         for (var t, n = [], r = /[\.?!](\s*\r|\s*\n|\s*(<\/em>)|\s*(?=<)|\s+(?=[A-ZА-Я]))/g, o = 0; null !== (t = r.exec(e)) && (end = r.lastIndex, !(end > m.sizeLimit));) n.push({
//             text: e.slice(o, end),
//             start: o,
//             end: end
//         }), o = end;
//         return e.length < m.sizeLimit && n.push({
//             text: e.slice(o),
//             start: o,
//             end: e.length
//         }), n.forEach(function(e) {
//             e.clean_text = d(e.text)
//         }), n
//     }

//     function d(e) {
//         return e = e.replace(/<em.*?>/g, ""), e = e.replace(/<\/em>/g, "")
//     }

//     function f(e, t) {
//         var n = [],
//             r = [];
//         return e.forEach(function(e) {
//             void 0 !== t[e.clean_text] ? n.push(e) : r.push(e)
//         }), {
//             old_chunks: n,
//             new_chunks: r
//         }
//     }

//     function v() {
//         var e = {},
//             t = [];
//         return $.each(C.getHints(), function(n, r) {
//             var o = $(r).data("rule");
//             if (y[o]) {
//                 var a = y[o].section;
//                 e[a] || (e[a] = 0, t.push(a)), e[a]++
//             }
//         }), t.sort(function(t, n) {
//             return e[n] - e[t]
//         }), t
//     }
//     var h = this,
//         m = $.extend({
//             process_url: "/@process/",
//             rules_url: "/@rules/",
//             csrf_token: "",
//             $sidebar: null,
//             sizeLimit: 2e4,
//             textProcessingDelay: 1e3
//         }, e),
//         p = h.glaveditor(),
//         C = p.data("glaveditor"),
//         y = {},
//         x = null,
//         w = {},
//         S = [],
//         _ = !1,
//         T = DelayedFunctionWithCancel(r, m.textProcessingDelay, o),
//         H = C.getHints(),
//         E = $('<div class="rule"></rule>').appendTo(m.$sidebar);
//     E.hide();
//     var b = null,
//         k = null,
//         R = null,
//         P = null,
//         z = null,
//         V = null,
//         A = 100;
//     p.on("glaveditor:mouseenterhint", function(e, t, n) {
//         V && clearTimeout(V), V = setTimeout(function() {
//             R = n, c(), V = null
//         }, A), e.stopPropagation()
//     }).on("glaveditor:mouseleavehint", function(e) {
//         V && clearTimeout(V), V = setTimeout(function() {
//             R = null, c(), V = null
//         }, A), e.stopPropagation()
//     }).on("glaveditor:caretenterhint", function(e, t, n) {
//         k = n, c(), e.stopPropagation()
//     }).on("glaveditor:caretleavehint", function(e) {
//         k = null, c(), e.stopPropagation()
//     }), p.on("glaveditor:change", function() {
//         _ = !1, T(), C.addClass("processing"), h.trigger("glavred:process", [B])
//     }), p.on("glaveditor:caretmove", function() {
//         _ = !1, x && (T(), C.addClass("processing"), h.trigger("glavred:process", [B]))
//     }), p.on("glaveditor:load", function() {});
//     var D = /(\.( |$))|([^\.\s]+$)/gm,
//         N = /[А-Яа-яA-Za-z0-9-]+([^А-Яа-яA-Za-z0-9-]+)?/g,
//         M = /[^А-Яа-яA-Za-z0-9-\s.,()-]+/g,
//         B = {
//             setHtml: function(e) {
//                 o(), C.setValue(e), r()
//          ь   },
//             setData: function(e, t, n) {
//                 o(), w = $.extend(w, t), y = $.extend(y, n), C.setValue(e), H = C.getHints(), r()
//             },
//             getText: function() {
//                 return C.getText()
//             },
//             getHtml: function() {
//                 return C.getHtml()
//             },
//             setHoverSection: function(e) {
//                 P = e, c()
//             },
//             setSelectedSection: function(e) {
//                 z = e, c()
//             },
//             focus: function() {
//                 return C.focus()
//             },
//             process: function() {
//                 r()
//             },
//             getStats: function() {
//                 for (var e = B.getText().trim(), t = C.getHints(), n = {
//                         score: 0,
//                         sentences: e ? e.match(D).length : 0,
//                         words: e ? e.replace(N, ".").length : 0,
//                         chars: e ? e.replace(M, "").length : 0,
//                         stopwords: t.length,
//                         textProcessed: _,
//                         sections: v(),
//                         0: 0
//                     }, r = t.map(function() {
//                         return y[$(this).data("rule")] ? y[$(this).data("rule")].penalty : void 0
//                     }), o = 0, a = 0; a < r.length; a++) o += r[a];
//                 return n.penalties = o, n.words ? window.ScoreFunc ? n.score = window.ScoreFunc(n) : (n.score = Math.floor(100 * Math.pow(1 - n.stopwords / n.words, 3)) - n.penalties, n.score = Math.min(Math.max(n.score, 0), 100), n.score = n.score % 10 == 0 ? n.score / 10 : (n.score / 10).toFixed(1)) : n.score = 0, n
//             }
//         };
//     return h.data("glavred", B), p.on("glaveditor:change", function() {
//         h.trigger("glavred:change", [B])
//     }), p.on("glaveditor:load", function() {
//         h.trigger("glavred:load", [B])
//     }), h
// }, $.fn.glaveditor = function() {
//     function e() {
//         var e = $(t(_.composer.element, _.composer.doc));
//         e.length && (T[0] != e[0] && (T.is(l) && i.trigger("glaveditor:caretleavehint", [a, T]), e.is(l) && i.trigger("glaveditor:caretenterhint", [a, e]), T = e), i.trigger("glaveditor:caretmove", [a]))
//     }

//     function t(e, t) {
//         return t || (t = window), t.getSelection().rangeCount > 0 ? t.getSelection().getRangeAt(0).commonAncestorContainer.parentNode : null
//     }

//     function n(e, t, n, r) {
//         return e.slice(0, n) + t + e.slice(r, e.length)
//     }

//     function r(e) {
//         var t = e == v || e == d || e == f || e == g || e == p || e == m || e == h || e == C || e == y || e == x;
//         return t
//     }
//     var o, a, i = this,
//         s = "<i></i>",
//         c = "i",
//         l = "em",
//         u = {
//             tags: {
//                 em: {
//                     check_attributes: {
//                         "data-rule": "alt"
//                     }
//                 },
//                 br: {},
//                 p: {},
//                 style: {
//                     remove: 1
//                 },
//                 a: {
//                     rename_tag: "span"
//                 }
//             }
//         },
//         g = 38,
//         d = 39,
//         f = 40,
//         v = 37,
//         h = 16,
//         m = 17,
//         p = 18,
//         C = 36,
//         y = 35,
//         x = 27,
//         w = $(null);
//     a = {
//         getHeight: function() {
//             return $(_.composer.iframe).outerHeight()
//         },
//         getValue: function() {
//             return w.html()
//         },
//         setValue: function(e) {
//             _.setValue(e), S = a.getText()
//         },
//         getText: function() {
//             var e = w[0].innerText || w[0].textContent;
//             return e
//         },
//         getHtml: function() {
//             return w.html()
//         },
//         addClass: function(e) {
//             w.addClass(e)
//         },
//         removeClass: function(e) {
//             w.removeClass(e)
//         },
//         hasClass: function(e) {
//             w.hasClass(e)
//         },
//         focus: function() {
//             return w.focus()
//         },
//         getHints: function() {
//             return w.find(l)
//         },
//         saveCaret: function() {
//             o.find(c).remove(), _.composer.selection.insertNode($(s)[0])
//         },
//         restoreCaret: function() {
//             var e = o.find(c)[0];
//             e && (_.composer.selection.selectNode(e), $(e).remove())
//         },
//         getCaretPosition: function() {
//             a.saveCaret();
//             var e = a.getValue().indexOf(s);
//             return o.find(c).remove(), e
//         },
//         setCaretPosition: function(e) {
//             var t = a.getValue();
//             t = n(t, s, e, e), a.setValue(t), a.restoreCaret()
//         },
//         surroundWithHTML: function(e, t, r, o) {
//             a.saveCaret();
//             var i = _.getValue();
//             i = n(i, o, t, t), i = n(i, r, e, e), _.setValue(i), a.restoreCaret()
//         },
//         getCaretElement: function() {
//             var e = $(t(_.composer.element, _.composer.doc));
//             if (e.length) return e
//         }
//     }, i.data("glaveditor", a), i.attr("id", "glaveditor-123123");
//     var S, _ = new wysihtml5.Editor(i.attr("id"), {
//         stylesheets: ["/static/glaveditor.css"],
//         parserRules: u
//     });
//     _.on("load", function() {
//         w = $(_.composer.element), o = $(_.composer.doc), S = a.getText(), w.on("copy", function(e) {
//             e.preventDefault();
//             var t = _.composer.doc.getSelection();
//             e.originalEvent.clipboardData.setData("text/plain", t)
//         }), w.on("keyup", function(n) {
//             var o = $(t(_.composer.element, _.composer.doc));
//             if (o.length)
//                 if (r(n.keyCode)) e();
//                 else {
//                     var s = a.getText();
//                     if (S == s) return;
//                     if (o.is(l + ",span,font")) {
//                         T.is(l) && i.trigger("glaveditor:caretleavehint", [a, T]), a.saveCaret();
//                         for (var c = o.html(); o.parent().is(l + ",span,font");) o = o.parent();
//                         o.replaceWith(c), a.restoreCaret(), e(), s = a.getText()
//                     }
//                     i.trigger("glaveditor:change", [a]), S = s
//                 }
//         }), w.on("mouseenter", l, function(e) {
//             i.trigger("glaveditor:mouseenterhint", [a, $(e.target)])
//         }), w.on("mouseleave", l, function(e) {
//             i.trigger("glaveditor:mouseleavehint", [a, $(e.target)])
//         }), w.on("click", function() {
//             e()
//         }), $(_.composer.iframe).wysihtml5_size_matters(), $(_.composer.iframe).data("wysihtml5_size_matters").adjustHeight(), i.trigger("glaveditor:load", [a])
//     }), _.on("paste:composer", function() {
//         i.trigger("glaveditor:change", [a])
//     });
//     var T = $(null);
//     return i
// }, $(function() {
//     (function() {
//         ! function(e) {
//             var t;
//             return t = function() {
//                 function t(t) {
//                     this.$iframe = e(t), this.$body = this.findBody(), this.addBodyStyles(), this.setupEvents(), this.adjustHeight()
//                 }
//                 return t.prototype.addBodyStyles = function() {
//                     return this.$body.css("overflow", "hidden"), this.$body.css("min-height", 0)
//                 }, t.prototype.setupEvents = function() {
//                     var e = this;
//                     return this.$body.on("keyup keydown paste change focus", function() {
//                         return e.adjustHeight()
//                     })
//                 }, t.prototype.adjustHeight = function() {
//                     return this.$iframe.css("min-height", this.$body.height() + this.extraBottomSpacing())
//                 }, t.prototype.extraBottomSpacing = function() {
//                     return parseInt(this.$body.css("line-height")) || this.estimateLineHeight()
//                 }, t.prototype.estimateLineHeight = function() {
//                     return 1.14 * parseInt(this.$body.css("font-size"))
//                 }, t.prototype.findBody = function() {
//                     return this.$iframe.contents().find("body")
//                 }, t
//             }(), e.fn.wysihtml5_size_matters = function() {
//                 return this.each(function() {
//                     var n;
//                     return n = e.data(this, "wysihtml5_size_matters"), n ? void 0 : n = e.data(this, "wysihtml5_size_matters", new t(this))
//                 })
//             }
//         }($)
//     }).call(this)
// });
// var saveSelection, restoreSelection, getCaretElement;
// window.getSelection && document.createRange ? (saveSelection = function(e) {
//     if (0 == window.getSelection().rangeCount) return null;
//     var t = window.getSelection().getRangeAt(0),
//         n = t.cloneRange();
//     n.selectNodeContents(e), n.setEnd(t.startContainer, t.startOffset);
//     var r = n.toString().length;
//     return {
//         start: r,
//         end: r + t.toString().length
//     }
// }, restoreSelection = function(e, t) {
//     if (null !== t) {
//         var n = 0,
//             r = document.createRange();
//         r.setStart(e, 0), r.collapse(!0);
//         for (var o, a = [e], i = !1, s = !1; !s && (o = a.pop());)
//             if (3 == o.nodeType) {
//                 var c = n + o.length;
//                 !i && t.start >= n && t.start <= c && (r.setStart(o, t.start - n), i = !0), i && t.end >= n && t.end <= c && (r.setEnd(o, t.end - n), s = !0), n = c
//             } else
//                 for (var l = o.childNodes.length; l--;) a.push(o.childNodes[l]);
//         var u = window.getSelection();
//         u.removeAllRanges(), u.addRange(r)
//     }
// }, getCaretElement = function() {
//     return window.getSelection().rangeCount > 0 ? window.getSelection().getRangeAt(0).commonAncestorContainer.parentNode : null
// }) : document.selection && (saveSelection = function(e) {
//     var t = document.selection.createRange(),
//         n = document.body.createTextRange();
//     n.moveToElementText(e), n.setEndPoint("EndToStart", t);
//     var r = n.text.length;
//     return {
//         start: r,
//         end: r + t.text.length
//     }
// }, restoreSelection = function(e, t) {
//     var n = document.body.createTextRange();
//     n.moveToElementText(e), n.collapse(!0), n.moveEnd("character", t.end), n.moveStart("character", t.start), n.select()
// }, getCaretElement = function() {
//     return null
// });
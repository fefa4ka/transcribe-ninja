// angular.module( 'stenograf', [
//   'ui.router'
// ])
// // API 
// .factory('glvrd', ["$http", "$resource", function($http, $resource){
//     var api_url = 'http://api.glvrd.ru/v1/',

//   return {
//     api: $resource(api_url, {}, {
//       status: { 
//         url: api_url + "status/",
//         params: { 
//             'key': '',
//             'token': '1436082595:POF-jRlNkIDHxg7IcfsYFqZCFm8'
//         },
//         method: 'GET' 
//       },
//       proof: { 
//         url: api_url + "proofread/",
//         params: { 
//             'key': '',
//             'token': '1436082595:POF-jRlNkIDHxg7IcfsYFqZCFm8'
//         },
//         method: 'GET' 
//       }
//     })
//   };
// }]);

// .directive('stenograf', function () { 
//   return {
//     restrict: 'E',
//     templateUrl: 'stenograf/stenograf.tpl.html',
//     link: function (scope, element, attrs) {
        

//     }
//   };
// })

// ;

// ! function() {
//     var e = function(e, n) {
//         function t(e) {
//             return {
//                 status: "error",
//                 code: e,
//                 message: i[e]
//             }
//         }

//         function r() {
//             return void 0 == a ? t("missing_jquery") : void 0
//         }
//         var o = "http://api.glvrd.ru/v1/",
//             u = {
//                 status: o + "status/",
//                 proofread: o + "proofread/"
//             },
//             a = window.jQuery,
//             i = {
//                 unreadable_response: "Пришел непонятный ответ от сервера",
//                 failed_request: "Запрос неудачен",
//                 missing_jquery: "Нужен jQuery"
//             },
//             s = null,
//             d = !1,
//             f = {
//                 getStatus: function(o) {
//                     var i = r();
//                     return i ? void o(i) : void(xhr = a.post(u.status, {
//                         key: e,
//                         token: n
//                     }).done(function(e) {
//                         o(void 0 === e.status ? t("unreadable_response") : e)
//                     }).fail(function() {
//                         o(t("failed_request"))
//                     }))
//                 },
//                 abortProofreading: function() {
//                     s && (d = !0, s.abort(), s = null)
//                 },
//                 proofread: function(o, i) {
//                     var f = r();
//                     return f ? void i(f) : void(s = a.post(u.proofread, {
//                         key: e,
//                         token: n,
//                         text: o
//                     }).done(function(e) {
//                         void 0 === e.status ? i(t("unreadable_response")) : (a.each(e.fragments, function(n, t) {
//                             t.hint = e.hints[t.hint];
//                             var r = o.slice(t.chunkStart, t.chunkEnd);
//                             t.url = "http://glvrd.ru/?text=" + encodeURIComponent(r), delete t.chunkStart, delete t.chunkEnd
//                         }), delete e.hints, i(e))
//                     }).fail(function() {
//                         d ? d = !1 : i(t("failed_request"))
//                     }).always(function() {
//                         s = null
//                     }))
//                 }
//             };
//         return f
//     };
//     window.glvrd = e("", "1436082595:POF-jRlNkIDHxg7IcfsYFqZCFm8")
// }();
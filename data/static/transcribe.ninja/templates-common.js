angular.module('templates-common', ['auth/auth.complete.tpl.html', 'auth/auth.login.modal.tpl.html', 'player/player.tpl.html']);

angular.module("auth/auth.complete.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("auth/auth.complete.tpl.html",
    "");
}]);

angular.module("auth/auth.login.modal.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("auth/auth.login.modal.tpl.html",
    "<form id=\"id_auth_form\" ng-submit=\"authLogin()\" ui-keypress=\"{13:'authLogin()'}\">\n" +
    "    \n" +
    "    <div class=\"modal-header\">\n" +
    "        <h3 class=\"modal-title text-line\" ng-hide=\"password_reset\">Вход через социальную сеть</h3>\n" +
    "        <h3 class=\"modal-title text-line\" ng-show=\"password_reset\">Восстановление пароля</h3>\n" +
    "    </div>\n" +
    "\n" +
    "    <div class=\"modal-body\">\n" +
    "            <div class=\"centered-text social-auth\" ng-hide=\"password_reset\">\n" +
    "                <a tabindex=\"1\" ng-click=\"popup('/api/social/login/vk-oauth/')\" title=\"Войти через Вконтакт\"><div class=\"social\" aria-hidden=\"true\" data-icon=\"&#xe003;\"></div></a>\n" +
    "                <a tabindex=\"2\" ng-click=\"popup('/api/social/login/facebook/')\" title=\"Войти через Фейсбук\"><div class=\"social\" aria-hidden=\"true\" data-icon=\"&#xe021;\"></div></a>\n" +
    "                <a tabindex=\"3\" ng-click=\"popup('/api/social/login/google-oauth2/')\" title=\"Войти через Google\"><div class=\"social\" aria-hidden=\"true\" data-icon=\"&#xe01b;\"></div></a>\n" +
    "                <h4 class=\"text-line\">или используя электронную почту</h4>\n" +
    "            </div>\n" +
    "\n" +
    "            <p ng-show=\"password_reset\">Мы вышлем ссылку для восстановления пароля на вашу почту</p>\n" +
    "            <p ng-show=\"password_reset_success\">Ссылка для востановления пароля отправлена вам на почту</p>\n" +
    "\n" +
    "            <div class=\"form-group\" ng-hide=\"password_reset_success\">\n" +
    "                <input tabindex=\"4\" ng-model=\"username\" required name=\"username\"\n" +
    "                       type=\"email\" placeholder=\"Адрес электронной почты\" alt=\"Войти через электронную почту\" class=\"form-control\"\n" +
    "                       id='auth_username'>\n" +
    "            </div>\n" +
    "\n" +
    "            <div class=\"auth-password\" ng-hide=\"password_reset\">\n" +
    "                <div class=\"form-group\">\n" +
    "                        <div class=\"btn-group\">\n" +
    "                            <label class=\"btn btn-default active\" ng-model=\"new_user\" btn-radio=\"'1'\" tabindex=\"5\">Я новый пользователь</label>\n" +
    "                            <label class=\"btn btn-default\" ng-model=\"new_user\" btn-radio=\"'2'\" tabindex=\"6\">Я уже зарегистрирован</label>\n" +
    "                        </div>\n" +
    "                    </div>\n" +
    "                <div class=\"form-group\" ng-show=\"new_user > 0\">\n" +
    "                    <input ng-model=\"password\" required name=\"password\" type=\"password\"\n" +
    "                           placeholder=\"Пароль\" alt=\"Пароль\" class=\"form-control\" tabindex=\"7\">\n" +
    "                </div>\n" +
    "                <div  class=\"form-group\" ng-show=\"new_user == 1\">\n" +
    "                    <input ng-model=\"repeat_password\" name=\"repeat_password\" type=\"password\"\n" +
    "                           placeholder=\"Повторите пароль\" alt=\"Повторить пароль\" class=\"form-control\" tabindex=\"8\"> \n" +
    "                </div>\n" +
    "                <div class=\"password-recovery text-line\" ng-show=\"new_user == 2\">\n" +
    "                    <a href=\"#\" ng-click=\"password_reset = 1\">Восстановить пароль</a>\n" +
    "                </div>\n" +
    "            </div>\n" +
    "    </div>\n" +
    "\n" +
    "    <div class=\"modal-footer\">\n" +
    "        <alert ng-repeat=\"alert in alerts\" type=\"{{ alert.type }}\" close=\"closeAlert($index)\">{{ alert.msg }}</alert>\n" +
    "        <input type=\"submit\" ng-hide=\"logining || password_reset\" class=\"btn btn-primary\" ng-value=\"new_user == 1 ? 'Зарегистрировать и войти' : 'Войти'\" alt=\"Войти\" tabindex=\"9\">\n" +
    "        <a ng-show=\"password_reset && password_reset_success === 0\" ng-click=\"passwordReset()\" class=\"btn btn-primary\" alt=\"Восстановить пароль\" tabindex=\"10\">Восстановить пароль</a>\n" +
    "\n" +
    "        <a ng-show=\"password_reset_success\" ng-click=\"cancel()\" class=\"btn btn-default\" alt=\"Закрыть\" tabindex=\"10\">Закрыть</a>\n" +
    "    </div>\n" +
    "\n" +
    "</form>\n" +
    "");
}]);

angular.module("player/player.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("player/player.tpl.html",
    "<div class=\"player\">\n" +
    "    <div class=\"progress progress-striped active\" ng-hide=\"loading_percent == 100\" width=\"{{ loading_percent }}%\">\n" +
    "        <div class=\"progress-bar progress-bar-info\"></div>\n" +
    "    </div>\n" +
    "\n" +
    "</div>\n" +
    "\n" +
    "    <button class=\"btn btn-default btn-circle play\" \n" +
    "            ng-click=\"wavesurfer.playPause()\">\n" +
    "        <i class=\"fa fa-play\"></i></button>");
}]);

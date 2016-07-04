angular.module('templates-app', ['history/detail/history.detail.tpl.html', 'history/history.tpl.html', 'history/payment/history.payment.tpl.html', 'main/main.logo.tpl.html', 'main/main.tpl.html', 'work/work.tpl.html']);

angular.module("history/detail/history.detail.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("history/detail/history.detail.tpl.html",
    "<div class=\"modal-header\">\n" +
    "    <h3 class=\"modal-title\">Обзор результатов</h3>\n" +
    "</div>\n" +
    "<div class=\"modal-body\">\n" +
    "    <h5>Ваша работа</h5>\n" +
    "    <p class=\"desc\">{{ queue.work_length }} символов напечатали и исправили</p>\n" +
    "    <pre ng-class=\"queue.work_type == 0 ? 'transcribed': 'checked'\" class=\"textdiff\" semantic-diff left-obj=\"diff.original_transcription\" right-obj=\"diff.transcription\"></pre>\n" +
    "    \n" +
    "    <div ng-show=\"queue.mistakes_length > 0\">\n" +
    "        <h5>После проверки</h5>\n" +
    "        <p class=\"desc\">{{ queue.mistakes_length }} символов исправили</p>\n" +
    "        <pre class=\"textdiff checked\" semantic-diff left-obj=\"diff.transcription\" right-obj=\"diff.checked_transcription\"></pre>\n" +
    "    </div>\n" +
    "\n" +
    "    <p class=\"desc\" ng-show=\"queue.checked && queue.mistakes_length == 0\">\n" +
    "        Вашу запись проверили, с ней всё впорядке\n" +
    "    </p>\n" +
    "\n" +
    "</div>\n" +
    "<div class=\"modal-footer\">\n" +
    "    <button class=\"btn btn-default\" ng-click=\"cancel()\">Закрыть</button>\n" +
    "</div>");
}]);

angular.module("history/history.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("history/history.tpl.html",
    "<h3>История вашей работы</h3>\n" +
    "<section class=\"queues row-fluid\">\n" +
    "    <div class=\"col-md-6 checked\">        \n" +
    "\n" +
    "\n" +
    "    <div ng-tabs>\n" +
    "        <ul class=\"list-unstyled list-inline tabs-menu\">\n" +
    "            <li ng-tab-head=\"active\">\n" +
    "                <h4><a href=\"#\" ng-click=\"$event.preventDefault()\">Ожидают проверки</a></h4>\n" +
    "                    <p ng-show=\"uncheckedStatistics.work_length > 0\">{{ uncheckedStatistics.work_length }} символов</p>\n" +
    "            </li>\n" +
    "\n" +
    "            <li ng-tab-head>\n" +
    "                <h4><a href=\"#\" ng-click=\"$event.preventDefault()\">Исправили</a></h4>\n" +
    "                    <p ng-show=\"total_checked.mistakes_length > 0\">{{ total_checked.mistakes_length }} символов</p>\n" +
    "            </li>\n" +
    "        </ul>\n" +
    "\n" +
    "\n" +
    "        <div ng-tab-body class=\"tab-body\">\n" +
    "            \n" +
    "                <p class=\"desc\">После того как мы проверим, что вы напечатали, вы сможете получить за эту работу деньги</p>\n" +
    "                <table class=\"table\" ng-show=\"uncheckedQueues.count > 0\">\n" +
    "                    <tr>\n" +
    "                        <th>Задача</th>\n" +
    "                        <th class=\"length\">Количество <small>символов</small></th>\n" +
    "                        <th class=\"length\">Заработано</th>\n" +
    "                    </tr>\n" +
    "                    <tr ng-repeat=\"queue in uncheckedQueues.results\" ng-mouseover=\"currentQueue = queue.id\">\n" +
    "                        <td class=\"work-type\">\n" +
    "                            {{ queue.duration | humanSeconds }} {{ queue.work_type == 0 ? \"транскрибации\" : \"вычитки\" }}\n" +
    "                            <a class=\"btn btn-xs btn-default pull-right\" ng-click=\"queueDetail(queue)\"><i class=\"fa fa-lg fa-align-left\"></i></a>\n" +
    "                        </td>\n" +
    "                        <td class=\"length\">\n" +
    "                            {{ queue.work_length }} \n" +
    "                        </td>\n" +
    "                        <td class=\"length\">\n" +
    "                            {{ queue.total_price | number : 2 }} ₽\n" +
    "                        </td>\n" +
    "                    </tr>\n" +
    "                </table>\n" +
    "                <pagination ng-show=\"uncheckedQueues.count > 10\" total-items=\"uncheckedQueues.count\" ng-model=\"$parent.uncheckedQueuePage\" max-size=\"10\" previous-text=\"&lsaquo;\" next-text=\"&rsaquo;\" ng-change=\"uncheckedPageChanged()\"></pagination>\n" +
    "        </div>\n" +
    "\n" +
    "        <div ng-tab-body class=\"tab-body\">\n" +
    "             <div ng-show=\"checkedQueues.count > 0\">\n" +
    "                    \n" +
    "                    <p class=\"desc\">Работу, которую мы проверили и в которой нашли ошибки</p>\n" +
    "\n" +
    "                    <table class=\"table\">\n" +
    "                        <tr>\n" +
    "                            <th>Задача</th>\n" +
    "                            <th class=\"length\">Набрано <small>символов</small></th>\n" +
    "                            <th class=\"length\">Исправлено <small>символов</small></th>\n" +
    "                            <th class=\"length\">Заработано</th>\n" +
    "                        </tr>\n" +
    "                        <tr ng-repeat=\"queue in checkedQueues.results\">\n" +
    "                            <td class=\"work-type\">\n" +
    "                                {{ queue.duration | humanSeconds }} {{ queue.work_type == 0 ? \"транскрибации\" : \"вычитки\" }}\n" +
    "                                <a class=\"btn btn-xs btn-default pull-right\" ng-click=\"queueDetail(queue)\"><i class=\"fa fa-lg fa-align-left\"></i></a>\n" +
    "                            </td>\n" +
    "                            <td class=\"length\">\n" +
    "                                {{ queue.work_length }} \n" +
    "                            </td>\n" +
    "                            <td class=\"length mistakes\">\n" +
    "                                {{ queue.mistakes_length  }}\n" +
    "                            </td>\n" +
    "                            <td class=\"length checked\">\n" +
    "                                {{ queue.total_price | number : 2 }} ₽\n" +
    "                            </td>\n" +
    "                        </tr>\n" +
    "                    </table>\n" +
    "                </div>\n" +
    "\n" +
    "                <pagination ng-show=\"checkedQueues.count > 10\" total-items=\"checkedQueues.count\" ng-model=\"$parent.checkedQueuePage\" max-size=\"10\" previous-text=\"&lsaquo;\" next-text=\"&rsaquo;\" ng-change=\"checkedPageChanged()\"></pagination>\n" +
    "        </div>\n" +
    "    </div>\n" +
    "       \n" +
    "\n" +
    "        \n" +
    "        \n" +
    "    </div>\n" +
    "    <div class=\"col-md-6\">\n" +
    "        <h4>Проверенная работа</h4>\n" +
    "        <p class=\"desc\" ng-show=\"total_checked.work_length > 0\">{{ total_checked.work_length }} символов</p>\n" +
    "        <p class=\"desc\">Оплачивается только проверенная работа<br/>Оцените сколько вы зарабатываете</p>\n" +
    "        <table class=\"table\" ng-show=\"statistics[statistics.length-1].work_length > 0\">\n" +
    "            <tr>\n" +
    "                <th>Период</th>\n" +
    "                <th class=\"length\">Напечатано <small>символов</small></th>\n" +
    "                <th class=\"length\">Исправлено <small>символов</small></th>\n" +
    "                <th class=\"length\">Заработано</th>\n" +
    "            </tr>\n" +
    "            <tr class=\"statistics\" ng-repeat=\"stat in statistics\" ng-show=\"stat.work_length > 0 && statistics[$index-1].work_length != stat.work_length\">\n" +
    "                <td>\n" +
    "                    {{ statisticsDescription[$index] }}\n" +
    "                </td>\n" +
    "                <td class=\"length\">\n" +
    "                    {{ stat.work_length }}\n" +
    "                </td>\n" +
    "                <td class=\"length mistakes\">\n" +
    "                    {{ stat.mistakes_length }}\n" +
    "                </td>\n" +
    "                <td class=\"length checked\">\n" +
    "                    {{ stat.total_price | number : 2 }} ₽\n" +
    "                </td>\n" +
    "            </tr>\n" +
    "        </table>\n" +
    "\n" +
    "\n" +
    "        <div ng-show=\"currentUser.checked_balance > 1 \">\n" +
    "            <h4>Платежи <a class=\"btn btn-xs btn-primary\" ng-click=\"takeMoney(currentUser.checked_balance)\">Получить деньги</a></h4>\n" +
    "            <div class=\"salary\">\n" +
    "                <p class=\"desc\"><strong>Вы можете получить {{ currentUser.checked_balance| number : 0 }} ₽</strong> на телефон, карточку, Яндекс.Деньги или QIWI</p>\n" +
    "                <p class=\"desc\" ng-show=\"currentUser.balance - currentUser.checked_balance > 0\">Остальные {{ currentUser.balance - currentUser.checked_balance | number : 0 }} ₽ сможете получить, когда мы проверим вашу работу</p>\n" +
    "            </div>\n" +
    "        </div>\n" +
    "        \n" +
    "        <p class=\"desc\" ng-show=\"(currentUser.balance - currentUser.checked_balance > 0) && currentUser.checked_balance <=1\">Мы ещё не проверили ваши {{ uncheckedStatistics.work_length }} символов, когда проверим вы сможете получить за них <strong>{{ currentUser.balance - currentUser.checked_balance | number : 2 }} ₽</strong?</p>\n" +
    "\n" +
    "\n" +
    "        <div class=\"payments-history\" ng-show=\"payments.count > 0\">\n" +
    "\n" +
    "            <h5>История операций с балансом</h5>\n" +
    "\n" +
    "            <table class=\"table\">\n" +
    "                <tr>\n" +
    "                    <th>Описание платежа</th>\n" +
    "                    <th class=\"length\">Сумма</th>\n" +
    "                    <th class=\"length\">Дата</th>\n" +
    "                </tr>\n" +
    "                <tr ng-repeat=\"payment in payments.results\">\n" +
    "                    <td class=\"work-type\">\n" +
    "                        {{ payment.comment }}\n" +
    "                    </td>\n" +
    "                    <td class=\"length checked\">\n" +
    "                        {{ payment.total | number : 2 }} ₽\n" +
    "                    </td>\n" +
    "                    <td>\n" +
    "                        {{ payment.created  | date : 'd MMM в HH:mm'   }}\n" +
    "                    </td>\n" +
    "                    \n" +
    "                </tr>\n" +
    "            </table>\n" +
    "            <pagination ng-show=\"payments.count > 10\" total-items=\"payments.count\" ng-model=\"paymentsPage\" max-size=\"10\" previous-text=\"&lsaquo;\" next-text=\"&rsaquo;\" ng-change=\"paymentsChanged()\"></pagination>\n" +
    "        </div>\n" +
    "    </div>\n" +
    "</section>");
}]);

angular.module("history/payment/history.payment.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("history/payment/history.payment.tpl.html",
    "<form ng-submit=\"takeMoney()\" ui-keypress=\"{13:'takeMoney()'}\">\n" +
    "<div ng-tabs>  \n" +
    "    <div class=\"modal-header\">\n" +
    "        <h3 class=\"modal-title text-line\">Оплата вашей работы</h3>\n" +
    "    </div>\n" +
    "\n" +
    "    <div class=\"modal-body\">\n" +
    "\n" +
    "\n" +
    "            <ul class=\"list-unstyled list-inline tabs-menu\">\n" +
    "                <li ng-tab-head=\"active\">\n" +
    "                    <h5><a href=\"#\" ng-click=\"$event.preventDefault()\">На телефон</a></h5>\n" +
    "                </li>\n" +
    "\n" +
    "                <li ng-tab-head>\n" +
    "                    <h5><a href=\"#\" ng-click=\"$event.preventDefault()\">На карту</a></h5>\n" +
    "                </li>\n" +
    "\n" +
    "                <li ng-tab-head>\n" +
    "                    <h5><a href=\"#\" ng-click=\"$event.preventDefault()\">QIWI Кошелёк</a></h5>\n" +
    "                </li>\n" +
    "\n" +
    "                <li ng-tab-head>\n" +
    "                    <h5><a href=\"#\" ng-click=\"$event.preventDefault()\">Яндекс.Деньги</a></h5>\n" +
    "                </li>\n" +
    "            </ul>\n" +
    "            \n" +
    "            <p>Мы перечислим вам <strong>{{ amount | number : 2 }} ₽ в течении суток</strong></p>\n" +
    "\n" +
    "            <div ng-tab-body class=\"tab-body\">\n" +
    "                 <div class=\"form-group\">\n" +
    "                    <input tabindex=\"4\" ng-model=\"$parent.phone\" required mask=\"(999) 999-99-99\" clean=\"true\"\n" +
    "                           type=\"text\" placeholder=\"Номер телефона\" alt=\"Номер телефона\" class=\"form-control\">\n" +
    "                </div>\n" +
    "            </div>\n" +
    "\n" +
    "            <div ng-tab-body class=\"tab-body\">\n" +
    "                 <div class=\"form-group\">\n" +
    "                    <input tabindex=\"4\" ng-model=\"$parent.card\" required mask=\"9999 9999 9999 9999\" clean=\"true\"\n" +
    "                           type=\"text\" placeholder=\"Номер карты\" alt=\"Номер карты\" class=\"form-control\">\n" +
    "                </div>\n" +
    "            </div>\n" +
    "\n" +
    "            <div ng-tab-body class=\"tab-body\">\n" +
    "                 <div class=\"form-group\">\n" +
    "                    <input tabindex=\"4\" ng-model=\"$parent.qiwi\" required mask=\"(999) 999-99-99\" clean=\"true\"\n" +
    "                           type=\"text\" placeholder=\"Номер телефона QIWI Кошелька\" alt=\"Номер телефона QIWI Кошелька\" class=\"form-control\">\n" +
    "                </div>\n" +
    "            </div>\n" +
    "\n" +
    "            <div ng-tab-body class=\"tab-body\">\n" +
    "                 <div class=\"form-group\">\n" +
    "                    <input tabindex=\"4\" ng-model=\"$parent.yandex\" required mask=\"9999999999999999\" clean=\"true\"\n" +
    "                           type=\"text\" placeholder=\"Номер кошелька Яндекс.Денег\" alt=\"Номер кошелька Яндекс.Денег\" class=\"form-control\">\n" +
    "                </div>\n" +
    "            </div>\n" +
    "\n" +
    "        </div>\n" +
    "            \n" +
    "           \n" +
    "\n" +
    "\n" +
    "\n" +
    "    <div class=\"modal-footer\">\n" +
    "        <alert ng-repeat=\"alert in alerts\" type=\"{{ alert.type }}\" close=\"closeAlert($index)\">{{ alert.msg }}</alert>\n" +
    "\n" +
    "        <a ng-click=\"cancel()\" class=\"btn btn-default pull-left\" alt=\"Закрыть\" tabindex=\"10\">Закрыть</a>\n" +
    "        <a ng-click=\"takeMoney(tabs.index)\" class=\"btn btn-primary pull-right\" alt=\"Получить деньги\" tabindex=\"10\">Получить деньги</a>\n" +
    "\n" +
    "    </div>\n" +
    "    </div>\n" +
    "</form>\n" +
    "");
}]);

angular.module("main/main.logo.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("main/main.logo.tpl.html",
    "  <svg width=\"400\" height=\"220\" version=\"1.1\"\n" +
    "     baseProfile=\"full\"\n" +
    "     xmlns=\"http://www.w3.org/2000/svg\"\n" +
    "     xmlns:xlink=\"http://www.w3.org/1999/xlink\">\n" +
    "    <defs>\n" +
    "        <path \n" +
    "            id=\"sloganSecondPath\" \n" +
    "            d=\"M0,44 C17,30 90,31 139,31 C189,31 263,0 263,0\"\n" +
    "            ></path>\n" +
    "        <path id=\"sloganFirstPath\" d=\"M0,44 C14,25 69,19 101,27 C132,34 197,58 233,14\"/>\n" +
    "    </defs>\n" +
    "   <!--    <animate id=\"animFirstPath_1\" xlink:href=\"#sloganFirstPath\"\n" +
    "        attributeName=\"d\"\n" +
    "        attributeType=\"XML\"\n" +
    "        from=\"M0,44 C14,20 69,19 101,27 C132,34 197,58 233,14\"\n" +
    "        to=\"M0,44 C14,10 69,19 101,27 C132,34 197,58 233,14\"\n" +
    "        begin=\"0s;animFirstPath_2.end\"\n" +
    "        dur=\"0.3s\" fill=\"freeze\" />\n" +
    "      <animate id=\"animFirstPath_2\" xlink:href=\"#sloganFirstPath\"\n" +
    "        attributeName=\"d\"\n" +
    "        attributeType=\"XML\"\n" +
    "        to=\"M0,44 C14,20 69,19 101,27 C132,34 197,58 233,14\"\n" +
    "        from=\"M0,44 C14,10 69,19 101,27 C132,34 197,58 233,14\"\n" +
    "        begin=\"animFirstPath_1.end\"\n" +
    "        dur=\"0.5s\" fill=\"freeze\" />\n" +
    "      \n" +
    "      <animate id=\"animSecondPath_1\" xlink:href=\"#sloganSecondPath\"\n" +
    "        attributeName=\"d\"\n" +
    "        attributeType=\"XML\"\n" +
    "        from=\"M0,44 C17,20 90,31 139,31 C189,31 263,-40 263,-20\"\n" +
    "        to=\"M0,44 C17,30 90,31 139,31 C189,31 263,-40 263,-20\"\n" +
    "        begin=\"0s;animSecondPath_2.end\"\n" +
    "        dur=\"0.4s\" fill=\"freeze\" />\n" +
    "      <animate id=\"animSecondPath_2\" xlink:href=\"#sloganSecondPath\"\n" +
    "        attributeName=\"d\"\n" +
    "        attributeType=\"XML\"\n" +
    "        to=\"M0,44 C17,20 90,31 139,31 C189,31 263,-40 263,-20\"\n" +
    "        from=\"M0,44 C17,30 90,31 139,31 C189,31 263,-40 263,-20\"\n" +
    "        begin=\"animSecondPath_1.end\"\n" +
    "      dur=\"0.3s\" fill=\"freeze\" /> -->\n" +
    "      <g id=\"logotype\">\n" +
    "        <text id=\"slogan_1\" transform=\"translate(185,0)\">\n" +
    "            <textPath xlink:href=\"#sloganFirstPath\">– РАСПОЗНАВАНИЕ РЕЧИ</textPath>\n" +
    "        </text>\n" +
    "        \n" +
    "        <text id=\"slogan_2\" transform=\"translate(200,10) rotate(10)\">\n" +
    "            <textPath xlink:href=\"#sloganSecondPath\">– СТЕНОГРАФИРОВАНИЕ</textPath>\n" +
    "        </text>\n" +
    "\n" +
    "        <g id=\"head\" transform=\"translate(0.000000, 0.000000)\">\n" +
    "            <path d=\"M120,218 C187,218 241,189 241,123 C241,56 169,62 130,0 C93,66 1,56 1,123 C1,189 53,218 120,218 Z\" id=\"silhouette\" fill=\"#000000\"></path>\n" +
    "            <path d=\"M31,146 C36,146 54,144 75,146 C89,146 90,150 116,150 C141,150 147,147 166,146 C187,145 207,146 212,146 C222,146 234,146 234,129 C234,98 221,83 201,83 C180,82 152,95 119,95 C92,95 68,94 48,93 C22,91 5,93 5,129 C5,148 23,146 31,146 Z\" id=\"eyes\" fill=\"#FFFFFF\"></path>\n" +
    "        </g>\n" +
    "        <text id=\"name\" x=\"15\" y=\"132\">\n" +
    "            <tspan id=\"name_1\" font-weight=\"700\">T</tspan>\n" +
    "            <tspan id=\"name_2\" font-weight=\"700\">r</tspan>\n" +
    "            <tspan id=\"name_3\" font-weight=\"400\">a</tspan>\n" +
    "            <tspan id=\"name_4\" font-weight=\"400\">n</tspan>\n" +
    "            <tspan id=\"name_5\" font-weight=\"400\">s</tspan>\n" +
    "            <tspan id=\"name_6\" font-weight=\"300\">c</tspan>\n" +
    "            <tspan id=\"name_7\" font-weight=\"300\">r</tspan>\n" +
    "            <tspan id=\"name_8\" font-weight=\"100\">i</tspan>\n" +
    "            <tspan id=\"name_9\" font-weight=\"100\">b</tspan>\n" +
    "            <tspan id=\"name_10\" font-weight=\"100\">e</tspan>\n" +
    "        </text>   \n" +
    "       <text id=\"ninja\" x=\"90\" y=\"190\" z-index=\"10\">ninja</text> \n" +
    "    </g>\n" +
    "</svg>");
}]);

angular.module("main/main.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("main/main.tpl.html",
    "<section class=\"mainpage\">\n" +
    "    <section class=\"col-md-offset-1 col-md-3 logo\">\n" +
    "        <img src=\"/static/assets/logo_slogan.svg\">\n" +
    "        \n" +
    "    </section>\n" +
    "    <section class=\"col-md-6 transcribe\">\n" +
    "        <a ui-sref=\"work\" class=\"btn btn-primary btn-xs work\" alt=\"Задания на транскрибацию\">Зарабатывайте</a>\n" +
    "        <p class=\"desc\">\n" +
    "            <nobr>Печатайте под диктовку,</nobr>\n" +
    "            <nobr>оплата за каждую букву</nobr>\n" +
    "        </p>\n" +
    "        <p ng-hide=\"true\">\n" +
    "            <strong>Около 1000 ₽ в день</strong>\n" +
    "        </p>\n" +
    "        \n" +
    "        <div class=\"controls\">\n" +
    "            <button class=\"btn btn-default btn-xs\" \n" +
    "                    ng-click=\"authModal()\"\n" +
    "                    ng-hide=\"currentUser.id\" alt=\"Войти\">Войти</button>\n" +
    "\n" +
    "            <div ng-show=\"currentUser.id\">\n" +
    "                <div class=\"btn-group\" dropdown>\n" +
    "                    <button type=\"button\" class=\"btn btn-default btn-xs dropdown-toggle\" dropdown-toggle ng-disabled=\"disabled\">{{ currentUser.username }} <span class=\"caret\"></span></button>\n" +
    "                    <ul class=\"dropdown-menu\" role=\"menu\">\n" +
    "                        <li>\n" +
    "                            <a ui-sref=\"history\">История вашей работы</a>\n" +
    "                        </li>\n" +
    "                        <li class=\"divider\"></li>\n" +
    "                        <li>\n" +
    "                            <a href=\"#\" ng-click=\"logout()\">Выход</a>\n" +
    "                        </li>\n" +
    "                    </ul>\n" +
    "                </div>\n" +
    "               <p class=\"balance\"> На счету: <strong>{{ currentUser.balance | number : 0 }} ₽</strong></p>\n" +
    "            </div>\n" +
    "        </div>\n" +
    "\n" +
    "    </section>\n" +
    "</section>");
}]);

angular.module("work/work.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("work/work.tpl.html",
    "\n" +
    "<div ng-show=\"queue.duration > 0\">\n" +
    "\n" +
    "<div class=\"instruction\" ng-show=\"queue.work_type == 0\">\n" +
    "    <h4>Напечатайте, что говорят в записи</h4>\n" +
    "</div>\n" +
    "\n" +
    "<div class=\"instruction\" ng-show=\"queue.work_type == 1\">\n" +
    "    <h4>Послушайте запись и исправьте ошибки в транскрибции</h2>\n" +
    "    <p class=\"desc\">\n" +
    "        За проверку заработаете <strong>{{ queue.total_price * 100 | number : 0 }} копеек</strong>, плюс <strong>1 копейка</strong> за каждое исправление.\n" +
    "    </p>\n" +
    "\n" +
    "</div>\n" +
    "\n" +
    "<div class=\"work-player\">\n" +
    "    <tn-player audio-file=\"{{ queue.audio_file }}\"></tn-player>    \n" +
    "\n" +
    "    <ul class=\"hotkeys-cheatsheet list-inline\">\n" +
    "        <li><span class=\"hotkeys-key\">esc</span> – проигрывать или пауза</li>\n" +
    "        <li><span class=\"hotkeys-key\">alt + &larr;</span> – перемотать назад</li>\n" +
    "        <li><span class=\"hotkeys-key\">alt + &rarr;</span> – перемотать вперёд</li>\n" +
    "    </ul>\n" +
    "</div>\n" +
    "\n" +
    "<div class=\"transcription row\">\n" +
    "    <div class=\"col-xs-9\">\n" +
    "        <p class=\"offset-top col-md-offset-1\" ng-show=\"queue.work_type && queue.offset_parts[0]\">...{{ queue.offset_parts[0] }}</p>\n" +
    "\n" +
    "        <ul class=\"queue-transcriptions\" ng-repeat=\"piece in queue.pieces\">\n" +
    "            <li class=\"row\" ng-repeat=\"transcription in piece.transcriptions\">\n" +
    "                <div class=\"speakers-block col-md-1\" ng-mouseover=\"transcription.speakerHover = 1\" ng-mouseleave=\"transcription.speakerHover = 0\">\n" +
    "                        <div class=\"speakers\" ng-show=\"transcription.speakerHover\" >\n" +
    "                            <div class=\"genders\">\n" +
    "                                <i class=\"speaker-3 fa\" ng-click=\"selectSpeaker(transcription, 3)\" ng-class=\"transcription.gender == 'F' ? 'fa-female' : 'fa-male'\"></i>\n" +
    "                                <i class=\"speaker-2 fa\" ng-click=\"selectSpeaker(transcription, 2)\" ng-class=\"transcription.gender == 'F' ? 'fa-female' : 'fa-male'\"></i>\n" +
    "                                <i class=\"speaker-1 fa\" ng-click=\"selectSpeaker(transcription, 1)\" ng-class=\"transcription.gender == 'F' ? 'fa-female' : 'fa-male'\"></i>\n" +
    "                            </div>\n" +
    "\n" +
    "                            <div class=\"genders\">\n" +
    "                                <i class=\"speaker-3 fa\" ng-click=\"selectSpeaker(transcription, 3, false)\" ng-class=\"transcription.gender == 'F' ? 'fa-male' : 'fa-female'\"></i>\n" +
    "                                <i class=\"speaker-2 fa\" ng-click=\"selectSpeaker(transcription, 2, false)\" ng-class=\"transcription.gender == 'F' ? 'fa-male' : 'fa-female'\"></i>\n" +
    "                                <i class=\"speaker-1 fa\" ng-click=\"selectSpeaker(transcription, 1, false)\" ng-class=\"transcription.gender == 'F' ? 'fa-male' : 'fa-female'\"></i>\n" +
    "                            </div>\n" +
    "                        </div>\n" +
    "                        \n" +
    "                        <i class=\"fa speaker\" ng-class=\"[transcription.gender == 'F' ? 'fa-female' : 'fa-male', transcription.speaker_code[1] > 0 ? 'speaker-' + transcription.speaker_code[1] : 'speaker-1']\"></i>\n" +
    "                    </a>\n" +
    "\n" +
    "                    <i class=\"triangle\"></i>\n" +
    "                </div>\n" +
    "                \n" +
    "                <div class=\"col-md-11 text-block\">\n" +
    "                    <textarea class=\"transcriptions msd-elastic\" data-ng-model=\"transcription.text\" data-piece=\"{{ piece.id }}\" data-index=\"{{ $index }}\" tabindex=\"1\"></textarea>\n" +
    "                </div>\n" +
    "\n" +
    "                <div class=\"clearfix visible-xs-block\"></div>\n" +
    "            </li>\n" +
    "\n" +
    "        </ul>\n" +
    "\n" +
    "        <ul class=\"queue-transcriptions\" ng-hide=\"(queue.work_type == 1 || queue.saving) && originalTranscriptions.length > 0\">\n" +
    "            <li class=\"row\">\n" +
    "                <div class=\"speakers-block col-md-1\" ng-mouseover=\"newTranscription.speakerHover = 1\" ng-mouseleave=\"newTranscription.speakerHover = 0\">\n" +
    "                        <div class=\"speakers\" ng-show=\"newTranscription.speakerHover\" >\n" +
    "                            <div class=\"genders\">\n" +
    "                                <i class=\"speaker-3 fa\" ng-click=\"selectSpeaker(newTranscription, 3)\" ng-class=\"newTranscription.gender == 'F' ? 'fa-female' : 'fa-male'\"></i>\n" +
    "                                <i class=\"speaker-2 fa\" ng-click=\"selectSpeaker(newTranscription, 2)\" ng-class=\"newTranscription.gender == 'F' ? 'fa-female' : 'fa-male'\"></i>\n" +
    "                                <i class=\"speaker-1 fa\" ng-click=\"selectSpeaker(newTranscription, 1)\" ng-class=\"newTranscription.gender == 'F' ? 'fa-female' : 'fa-male'\"></i>\n" +
    "                            </div>\n" +
    "\n" +
    "                            <div class=\"genders\">\n" +
    "                                <i class=\"speaker-3 fa\" ng-click=\"selectSpeaker(newTranscription, 3, false)\" ng-class=\"newTranscription.gender == 'F' ? 'fa-male' : 'fa-female'\"></i>\n" +
    "                                <i class=\"speaker-2 fa\" ng-click=\"selectSpeaker(newTranscription, 2, false)\" ng-class=\"newTranscription.gender == 'F' ? 'fa-male' : 'fa-female'\"></i>\n" +
    "                                <i class=\"speaker-1 fa\" ng-click=\"selectSpeaker(newTranscription, 1, false)\" ng-class=\"newTranscription.gender == 'F' ? 'fa-male' : 'fa-female'\"></i>\n" +
    "                            </div>\n" +
    "                        </div>\n" +
    "                        \n" +
    "                        <i class=\"fa speaker\" ng-class=\"[newTranscription.gender == 'F' ? 'fa-female' : 'fa-male', newTranscription.speaker_code[1] > 0 ? 'speaker-' + newTranscription.speaker_code[1] : 'speaker-1']\"></i>\n" +
    "                    </a>\n" +
    "\n" +
    "                    <i class=\"triangle\"></i>\n" +
    "                </div>\n" +
    "                \n" +
    "                <div class=\"col-md-11 text-block\">\n" +
    "                    <textarea id=\"new-transcription\" class=\"transcriptions msd-elastic\" data-ng-model=\"newTranscription.text\" autofocus tabindex=\"2\"></textarea>\n" +
    "                </div>\n" +
    "            </li>\n" +
    "        </ul>\n" +
    "        \n" +
    "        <p class=\"offset-bottom col-md-offset-1\" ng-show=\"queue.work_type && queue.offset_parts[1]\">{{ queue.offset_parts[1] }}...</p>\n" +
    "        \n" +
    "        \n" +
    "        <section class=\"controls col-md-offset-1\">\n" +
    "            <ul class=\"list-unstyled pull-left\">\n" +
    "                <li>\n" +
    "                    <button class=\"skip btn btn-default btn-xs\" \n" +
    "                    ng-click=\"loadQueue(true)\" tabindex=\"5\">Пропустить задачу</button>\n" +
    "                </li>\n" +
    "                <li ng-show=\"queue.work_type == 0\"><p class=\"desc\">Можете пропустить задачу просто так<br/>или если запись пустая или речь неразборчивая, пометьте это</p></li>\n" +
    "                <li ng-show=\"queue.work_type == 0\"><a class=\"btn btn-warning btn-xs\" ng-click=\"poorRecord()\" tabindex=\"6\">Запись неразборчивая</a></li>     \n" +
    "            </ul>\n" +
    "            <!--  -->\n" +
    "\n" +
    "            <div class=\"pull-right\">\n" +
    "                <p>\n" +
    "                    Заработали <strong>{{ earnMoneyValue() | number : 2 }} ₽</strong>\n" +
    "                </p>\n" +
    "                <button class=\"btn btn-primary\" \n" +
    "                        ng-click=\"saveTranscription()\" tabindex=\"3\">Отправить на проверку</button>\n" +
    "                <p>\n" +
    "                    <kbd>ctrl+enter</kbd>\n" +
    "                </p>\n" +
    "            </div>\n" +
    "            \n" +
    "        </section>\n" +
    "    </div>\n" +
    "    <div class=\"col-xs-3\">\n" +
    "        <section class=\"suggest\">\n" +
    "            <h6>Случайный совет</h6>\n" +
    "            <p ng-bind-html=\"suggest\" tabindex=\"4\"></p>\n" +
    "        </section>\n" +
    "    </div>\n" +
    "</div>\n" +
    "\n" +
    "</div>");
}]);

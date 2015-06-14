angular.module( 'transcribe-ninja.localization', [
  'pascalprecht.translate'
])

.filter("secondsHms", function() {
    var format = function(seconds) {

    };

    return function (totalSeconds) {
        var hours   = Math.floor(totalSeconds / 3600);
        var minutes = Math.floor((totalSeconds - (hours * 3600)) / 60);
        var seconds = totalSeconds - (hours * 3600) - (minutes * 60);

        // round seconds
        seconds = Math.round(seconds * 100 / 100);

        var result = "";
        if(hours > 0) {
            result = (hours < 10 ? "0" + hours : hours) + ":";
        }
    
        result += (minutes < 10 ? "0" + minutes : minutes) + ":";
        result += (seconds  < 10 ? "0" + seconds : seconds);

        return result;
    };
})

.filter("humanSeconds", ["$filter", function ($filter) {
    var minute = 60;
    var hour = minute * 60;
    var day = hour * 24;
    var week = day * 7;
    var year = day * 365;
    var month = year / 12;
    var format = function(number, text) {
        
        text += "_" + (1 == number % 10 && 11 != number % 100 ? 0 : 2 <= number % 10 && 4 >= number % 10 && (10 > number % 100 || 20 <= number % 100) ? 1 : 2);

        text = "{{num}} " + text;

        return $filter("translate")(text, {num: number});
    };

    return function (seconds) {
        seconds = Math.round(seconds);
        
        switch (false) {
        case (seconds < minute) === false:
            return format(seconds, "second");
        case (seconds < hour) === false:
            return format(Math.floor(seconds / minute), "minute");
        case (seconds < day) === false:
            return format(Math.floor(seconds / hour), "hour");
        case (seconds < week) === false:
            return format(Math.floor(seconds / day), "day");
        case (seconds < month) === false:
            return format(Math.floor(seconds / week), "week");
        case (seconds < year) === false:
            return format(Math.floor(seconds / month), "month");
        default:
            return format(Math.floor(seconds / year), "year");
        }
    };
}])

.config(["$translateProvider", function($translateProvider) {

    $translateProvider
    .translations("en", {
        "{{num}} second":   "{{num}} second",
        "{{num}} seconds":  "{{num}} seconds",
        "{{num}} minute":   "{{num}} minute",
        "{{num}} minutes":  "{{num}} minutes",
        "{{num}} hour":     "{{num}} hour",
        "{{num}} hours":    "{{num}} hours",
        "{{num}} day":      "{{num}} day",
        "{{num}} days":     "{{num}} days",
        "{{num}} week":     "{{num}} week",
        "{{num}} weeks":    "{{num}} weeks",
        "{{num}} month":    "{{num}} month",
        "{{num}} months":   "{{num}} months",
        "{{num}} year":     "{{num}} year",
        "{{num}} years":    "{{num}} years"
    });

    $translateProvider
    .translations('ru', {
        'Стенограф': 'Transcribe',
        HEADLINE: 'Hello there, This is my awesome app!',
        INTRO_TEXT: 'And it has i18n support!',
        'Female': 'Женщина',
        'Male': 'Мужчина',
          "{{num}} second_0": "{{num}} секунда",
          "{{num}} second_1":  "{{num}} секунды",
        "{{num}} second_2":  "{{num}} секунд",
        "{{num}} minute_0": "{{num}} минута",
        "{{num}} minute_1": "{{num}} минуты",
        "{{num}} minute_2":  "{{num}} минут",
        "{{num}} hour_0": "{{num}} час",
        "{{num}} hour_1": "{{num}} часа",
        "{{num}} hour_2":  "{{num}} часов",
        "{{num}} hour":   "{{num}} час",
        "{{num}} hours":  "{{num}} часов",
        "{{num}} day":    "{{num}} day",
        "{{num}} days":   "{{num}} days",
        "{{num}} week":   "{{num}} week",
        "{{num}} weeks":  "{{num}} weeks",
        "{{num}} month":  "{{num}} month",
        "{{num}} months": "{{num}} months",
        "{{num}} year":   "{{num}} year",
        "{{num}} years":  "{{num}} years"
    });
}]);
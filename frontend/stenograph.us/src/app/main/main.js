angular.module( 'transcribe-ninja.main', [
  'transcribe-ninja.feedback',
  'ui.router',
  'ngMask'
])

.config(["$stateProvider", function config( $stateProvider ) {
  $stateProvider.state( 'main', {
    url: '/',
    views: {
      "main": {
        controller: 'MainCtrl',
        templateUrl: 'main/main.tpl.html'
      }
    },
    data:{ pageTitle: 'Стенографирование разговоров' }
  });
}])

.controller( 'MainCtrl', ["$scope", "$translate", "SmartPlurals", "$modal", function MainCtrl( $scope, $translate, SmartPlurals, $modal) {
  $translate.use("ru");
  var pluralRule = SmartPlurals.getRule('ru');

  $scope.calculator_hours = 1;


  $scope.select_calculator = function () {
    var $calculator = $("#calculator");

    yaCounter30919251.reachGoal('calculator');

    setTimeout(function () { $("#calculator").select(); }, 50); //select all text in any field on focus for easy re-entry. Delay sightly to allow focus to "stick" before selecting.

  }

  $scope.calculator = function (hours) {
    var price = 12;

    return hours * price * 60
  }

  $scope.callback = function (record) {
    yaCounter30919251.reachGoal('callback-open');

    $modalInstance = $modal.open(
    {
      templateUrl: 'feedback/callback.modal.tpl.html',
      controller: 'FeedbackModalCtrl',
      windowClass: 'feedback-callback',
      resolve: {
        title: function () {
          return "Обратный звонок";
        },
        description: function () {
          return "Оставьте свой номер телефона, мы сейчас вам перезвоним";
        }
      }
    });
  };

  $scope.upload = function (record) {
    yaCounter30919251.reachGoal('main-upload');

    $modalInstance = $modal.open(
    {
      templateUrl: 'main/main.upload.modal.tpl.html',
      controller: 'MainUploadModalCtrl',
      windowClass: 'main-upload',
      resolve: {
        callback: function () {
          return $scope.callback;
        },
        uploader: function () {
          return $scope.uploader;
        }
      }
    });
  };

  // select_file = document.getElementById('select_file')

  // select_file.onclick = charge

  // function charge()
  // {
  //   document.body.onfocus = roar
  // }

  // function roar()
  // {
  //   console.log(select_file, $scope);
  //   if($scope.$$childHead.uploader.queue.length) alert('ROAR! FILES!')
  //   else alert('*empty wheeze*')
  //   document.body.onfocus = null
  //   console.log('depleted')
  // }
}])


.controller( 'MainUploadModalCtrl', ["$scope", "$rootScope", "$modalInstance", "$modal", "api", "callback", "uploader", function MainUploadModalCtrl( $scope, $rootScope, $modalInstance, $modal, api, callback, uploader ) {
    console.log($scope);
    $scope.callback = callback;
    $scope.uploader = $rootScope.uploader;

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.callback = function (record) {
      yaCounter30919251.reachGoal('callback-open-upload');

      $modalInstance = $modal.open(
      {
        templateUrl: 'feedback/callback.modal.tpl.html',
        controller: 'FeedbackModalCtrl',
        windowClass: 'feedback-callback',
        resolve: {
          title: function () {
            return "Обратный звонок";
          },
          description: function () {
            return "Мы можем обсудить особые условия и ответить на ваши вопросы. Оставьте свой номер телефона, мы вам перезвоним";
          }
        }
      });
    };

    // $scope.sendFeedback = function (payment_type) {
    //     var destination = "";

    //     yaCounter30919251.reachGoal('feedback-send');

    //     api.feedback.create({
    //         email: $scope.email,
    //         phone: $scope.phone,
    //         subject: $scope.subject,
    //         text: $scope.text
    //     }, function () {
    //         if(angular.isUndefined($scope.callback) === false) {
    //             $scope.callback();
    //         }
    //     });

        
    //     $modalInstance.dismiss('cancel');


    // };

}])


;

angular.module( 'transcribe-ninja.feedback', [
  'ui.router',
  'ngMask'
])

.config(["$stateProvider", function config( $stateProvider ) {

}])

.controller( 'FeedbackModalCtrl', ["$scope", "$modalInstance", "api", "title", "description", function FeedbackModalCtrl( $scope, $modalInstance, api, title, description ) {
    $scope.title = title;
    $scope.description = description;
    
    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.sendFeedback = function (payment_type) {
        var destination = "";

        yaCounter30919251.reachGoal('feedback-send');

        api.feedback.create({
            email: $scope.email,
            phone: $scope.phone,
            subject: $scope.subject,
            text: $scope.text
        }, function () {
            if(angular.isUndefined($scope.callback) === false) {
                $scope.callback();
            }
        });

        
        $modalInstance.dismiss('cancel');


    };

}])

;

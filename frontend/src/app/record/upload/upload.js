angular.module( 'transcribe-ninja.record.upload', [
  'transcribe-ninja.player',
  'ui.router',
  'angularFileUpload'
  ])

.config(function config( $stateProvider ) {
  $stateProvider.state( 'record-upload', {
    url: '/upload',
    views: {
      "main": {
        controller: 'RecordUploadCtrl',
        templateUrl: 'record/upload/upload.tpl.html'
      }
    },
    data:{ pageTitle: 'Загрузка записи' }
  });
})
.filter('trusted', ['$sce', function ($sce) {
    return function(url) {
        return $sce.trustAsResourceUrl(url);
    };
}])

.directive('tnGetDuration', function (Data) {
  return {
    link: function (scope, element, attrs) {
      element.on('canplaythrough', function (e) {
        scope.item.formData[0].duration = e.target.duration;
        scope.$apply();
      });
    }
  };
})

.controller( 'RecordUploadCtrl', function RecordUploadCtrl($scope, $translate, $modal, FileUploader, $log, api ) {
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }

  var uploader = $scope.uploader = new FileUploader({
    url: '/api/records/',
    alias: 'audio_file',
    headers : {
        'X-CSRFToken': getCookie('csrftoken') // X-CSRF-TOKEN is used for Ruby on Rails Tokens
    }
  }),

  $modalInstance = {};


  $scope.open = function(){
    $modalInstance = $modal.open({
      templateUrl: 'record/upload/upload.list.tpl.html',
      windowClass: 'upload-modal',
      controller: function($scope, $modalInstance, $log, uploader){
        $scope.uploader = uploader;

        $scope.cancel = function () {
          $modalInstance.dismiss('cancel');

          uploader.cancelAll();
        };
    },
    resolve: {
        uploader: function () {
          return uploader;
        }
      },
      size: 'lg'
    });
  };


  uploader.onWhenAddingFileFailed = function(item /*{File|FileLikeObject}*/, filter, options) {
      console.info('onWhenAddingFileFailed', item, filter, options);
  };

  uploader.onAfterAddingFile = function(fileItem) {
      console.info('onAfterAddingFile', fileItem);

      fileItem.formData.push({
          title: fileItem.file.name,
          speakers: fileItem.file.speakers,
          file: URL.createObjectURL(fileItem._file),
          duration: 0
      });

  };
  uploader.onAfterAddingAll = function(addedFileItems) {
      $scope.open();

      console.info('onAfterAddingAll', addedFileItems);
  };
  
  uploader.onBeforeUploadItem = function(item) {
      console.info('onBeforeUploadItem', item);
  };
  uploader.onProgressItem = function(fileItem, progress) {
      console.info('onProgressItem', fileItem, progress);
  };
  uploader.onProgressAll = function(progress) {
      console.info('onProgressAll', progress);
  };
  uploader.onSuccessItem = function(fileItem, response, status, headers) {
      console.info('onSuccessItem', fileItem, response, status, headers);
  };
  uploader.onErrorItem = function(fileItem, response, status, headers) {
      console.info('onErrorItem', fileItem, response, status, headers);
  };
  uploader.onCancelItem = function(fileItem, response, status, headers) {
      console.info('onCancelItem', fileItem, response, status, headers);
  };
  uploader.onCompleteItem = function(fileItem, response, status, headers) {
      console.info('onCompleteItem', fileItem, response, status, headers);
  };

  uploader.onCompleteAll = function() {
      uploader.queue = [];
      $modalInstance.dismiss('cancel');
  };

})

;

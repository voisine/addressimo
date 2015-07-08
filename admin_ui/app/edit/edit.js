'use strict';

angular.module('addressimoUI.edit', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/edit', {
    templateUrl: 'edit/edit.html',
    controller: 'EditCtrl'
  });
}])

.controller('EditCtrl', ['$location', '$scope', 'GenericAPIService', function($location, $scope, GenericAPIService) {

    $scope.data = {};
    $scope.message = $scope.error_message = null;

    $scope.loadID = function(id) {
        var get_func = GenericAPIService.createServicePromise('/api/' + id, 'GET', 'Unable to get id object');

        get_func().then(function(response) {
            if(response.iserror) {
                $scope.error_message = response.message;
            } else {
                $scope.data = response.data.data;
            }
        })
    };

    $scope.init = function() {
        if (angular.isDefined($location.search().id)) {
            $scope.loadID($location.search().id);
        }
    };

    $scope.save = function() {

        $scope.message = null;
        var api_func;

        if (angular.isDefined($scope.data.id)) {
            api_func = GenericAPIService.createServicePromise('/api/' + $scope.data.id, 'PUT', 'Unable to save id object');
        } else {
            api_func = GenericAPIService.createServicePromise('/api', 'POST', 'Unable to create id object');
        }

        api_func($scope.data).then(function(response) {
            if(response.iserror) {
                $scope.error_message = response.message;
            } else {
                $scope.message = response.data.message;

                $scope.loadID(response.data.id);
            }
        })
    };

    $scope.deletePrivKey = function() {

        $scope.message = null;

        var delete_func = GenericAPIService.createServicePromise('/api/' + $scope.data.id + '/privkey', 'DELETE', 'Unable to delete private key.');

        delete_func().then(function(response) {
            if(response.iserror) {
                $scope.error_message = response.message;
            } else {
                $scope.message = response.message;
            }
        })
    };

    $scope.delete = function() {

        $scope.message = null;

        var delete_func = GenericAPIService.createServicePromise('/api/' + $scope.data.id, 'DELETE', 'Unable to delete id object.');

        delete_func().then(function(response) {
            if(response.iserror) {
                $scope.error_message = response.message;
            } else {
                $scope.message = response.message;
            }
        })
    };

    $scope.init();
}]);
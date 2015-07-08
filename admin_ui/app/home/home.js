'use strict';

angular.module('addressimoUI.home', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/home', {
    templateUrl: 'home/home.html',
    controller: 'HomeCtrl'
  });
}])

.controller('HomeCtrl', ['$scope', 'GenericAPIService', function($scope, GenericAPIService) {

    $scope.error_message = null;

    $scope.loadIds = GenericAPIService.createServicePromise('/api', 'GET', 'Unable to get id objects');

    $scope.loadIds().then(function(response) {
        if(response.iserror) {
            $scope.error_message = response.message;
        } else {
            $scope.keys = response.data.keys;
        }
    });

}]);
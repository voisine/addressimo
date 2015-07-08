
'use strict';

angular.module('addressimoUI.apiService', [])

    .factory('GenericAPIService', ['$http', '$location', function($http, $location) {

        var service = {
            $http: $http,
            $location: $location
        };

        service.createServicePromise = function(url, method, errMsg) {

            return function(data) {

                var url_port = 5000;
                if(service.$location.host() != 'localhost') {
                    url_port = service.$location.port();
                }

                var options = {
                    url: service.$location.protocol() + '://' + service.$location.host() +':' + url_port + url,
                    method: method,
                    headers: {'Content-Type': 'application/json'}
                };

                if (angular.isDefined(data)) {
                    options.data = data;
                }

                var promise = service.$http(options).then(function(response) {
                    if([200,201,202].indexOf(response.status) > -1 && response.data.success) {
                        return {iserror: false, data: response.data};
                    } else if (response.status == 204) {
                        return {iserror: false, message: 'object deleted'}
                    } else {
                        return {iserror: true, message: response.data.message}
                    }
                }, function(err) {
                    if(angular.isDefined(err.data) && angular.isDefined(err.data.message)) {
                        if(angular.isDefined(err.data.failures) && err.data.failures.length > 0) {
                            return {iserror: true, message: err.data.failures[0].message};
                        } else {
                            return {iserror: true, message: err.data.message};
                        }
                    }
                    return {iserror: true, message: errMsg}
                });
                return promise;
            };

        };

        return service;
    }]);
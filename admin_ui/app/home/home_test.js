'use strict';

describe('addressimoUI.home module', function() {

  beforeEach(module('addressimoUI.home'));

  describe('HomeCtrl controller', function() {

    var HomeCtrl, mockScope, mockGenericAPIService, promise_func, mockLocation;
    var return_data = {};

    // Promise handling for GenericAPIService mocked response
    beforeEach(function() {
      var intFunc, ret_obj;

      intFunc = function(test_fn) {
          test_fn(return_data);
      };

      ret_obj = {
          then: intFunc
      };

      promise_func = jasmine.createSpy('promise_func');
      promise_func.and.returnValue(ret_obj);

      mockGenericAPIService = jasmine.createSpyObj('GenericAPIService', ['createServicePromise']);
      mockGenericAPIService.createServicePromise.and.returnValue(promise_func);
      module(function($provide) {
          $provide.value('GenericAPIService', mockGenericAPIService);
      });

    });

    describe('loadID() tests', function() {
      it('tests the go right case', function() {
        inject(function($controller, $rootScope) {
          mockScope = $rootScope.$new();

          return_data = {data:{keys:['1', '2']}};

          HomeCtrl = $controller('HomeCtrl', {
            $scope: mockScope,
            GenericAPIService: mockGenericAPIService
          });

        });

        expect(mockGenericAPIService.createServicePromise).toHaveBeenCalledWith('/api', 'GET', 'Unable to get id objects');
        expect(mockScope.keys).toEqual(['1', '2']);
        expect(mockScope.error_message).toBeNull();
      });

      it('tests the iserror case', function() {

        inject(function($controller, $rootScope) {
          mockScope = $rootScope.$new();

          return_data = {iserror: true, message: 'id_obj not found'};

          HomeCtrl = $controller('HomeCtrl', {
            $scope: mockScope,
            GenericAPIService: mockGenericAPIService
          });
        });

        expect(mockGenericAPIService.createServicePromise).toHaveBeenCalledWith('/api', 'GET', 'Unable to get id objects');
        expect(mockScope.keys).toBeUndefined();
        expect(mockScope.error_message).toEqual('id_obj not found');
      });
    });
  });
});
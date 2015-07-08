'use strict';

describe('addressimoUI.edit module', function() {

  beforeEach(module('addressimoUI.edit'));

  describe('EditCtrl controller', function() {

    var EditCtrl, mockScope, mockGenericAPIService, promise_func, mockLocation;
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

    // Setup controller and handle first run $location data
    beforeEach(inject(function($controller, $location, $rootScope) {
      mockLocation = jasmine.createSpyObj('$location', ['search']);
      mockLocation.search.and.returnValue({});
      mockScope = $rootScope.$new();

      EditCtrl = $controller('EditCtrl', {
        $location: mockLocation,
        $scope: mockScope,
        GenericAPIService: mockGenericAPIService
      });

    }));

    describe('loadID() tests', function() {
      it('tests the go right case', function() {
        return_data = {data:{data:'id_obj'}};

        mockScope.loadID('id');

        expect(mockGenericAPIService.createServicePromise).toHaveBeenCalledWith('/api/id', 'GET', 'Unable to get id object');
        expect(mockScope.data).toEqual('id_obj');
        expect(mockScope.error_message).toBeNull();
      });

      it('tests the iserror case', function() {
        return_data = {iserror: true, message: 'id_obj not found'};

        mockScope.loadID('id');

        expect(mockGenericAPIService.createServicePromise).toHaveBeenCalledWith('/api/id', 'GET', 'Unable to get id object');
        expect(mockScope.data).toEqual({});
        expect(mockScope.error_message).toEqual('id_obj not found');
      });

      it('tests that loadID is called with the query parameter id if present', function() {
        spyOn(mockScope, 'loadID');
        mockLocation.search.and.returnValue({id: 'queryid'});

        mockScope.init();

        expect(mockScope.loadID).toHaveBeenCalledWith('queryid');
      });
    });

    describe('save() tests', function() {
      it('tests the POST (create) go right case', function() {
        spyOn(mockScope, 'loadID');
        return_data = {data: {message: 'message', id: 'id'}};

        mockScope.save();

        expect(mockGenericAPIService.createServicePromise).toHaveBeenCalledWith('/api', 'POST', 'Unable to create id object');
        expect(mockScope.message).toEqual('message');
        expect(mockScope.error_message).toBeNull();
        expect(mockScope.loadID).toHaveBeenCalledWith('id');
      });

      it('tests the PUT (update) go right case', function() {
        spyOn(mockScope, 'loadID');
        mockScope.data = {id: 'id'};
        return_data = {data: {message: 'message', id: 'id'}};

        mockScope.save();

        expect(mockGenericAPIService.createServicePromise).toHaveBeenCalledWith('/api/id', 'PUT', 'Unable to save id object');
        expect(mockScope.message).toEqual('message');
        expect(mockScope.error_message).toBeNull();
        expect(mockScope.loadID).toHaveBeenCalledWith('id');
      });

      it('tests the iserror response case', function() {
        spyOn(mockScope, 'loadID');
        return_data = {iserror: true, message: 'Update error'};

        mockScope.save();

        expect(mockGenericAPIService.createServicePromise).toHaveBeenCalledWith('/api', 'POST', 'Unable to create id object');
        expect(mockScope.message).toBeNull();
        expect(mockScope.error_message).toEqual('Update error');
        expect(mockScope.loadID).not.toHaveBeenCalled();
      });
    });

    describe('deletePrivKey() tests', function() {
      it('tests the go right case', function() {
        mockScope.data.id = 'id';
        return_data = {message: 'message'};

        mockScope.deletePrivKey();

        expect(mockGenericAPIService.createServicePromise).toHaveBeenCalledWith('/api/id/privkey', 'DELETE', 'Unable to delete private key.');
        expect(mockScope.message).toEqual('message');
        expect(mockScope.error_message).toBeNull();
      });

      it('tests the iserror response case', function() {
        mockScope.data.id = 'id';
        return_data = {iserror: true, message: 'Error during delete'};

        mockScope.deletePrivKey();

        expect(mockGenericAPIService.createServicePromise).toHaveBeenCalledWith('/api/id/privkey', 'DELETE', 'Unable to delete private key.');
        expect(mockScope.message).toBeNull();
        expect(mockScope.error_message).toEqual('Error during delete');
      });
    });

    describe('delete() tests', function() {
      it('tests the go right case', function() {
        mockScope.data.id = 'id';
        return_data = {message: 'message'};

        mockScope.delete();

        expect(mockGenericAPIService.createServicePromise).toHaveBeenCalledWith('/api/id', 'DELETE', 'Unable to delete id object.');
        expect(mockScope.message).toEqual('message');
        expect(mockScope.error_message).toBeNull();
      });

      it('tests the iserror response case', function() {
        mockScope.data.id = 'id';
        return_data = {iserror: true, message: 'Error during delete'};

        mockScope.delete();

        expect(mockGenericAPIService.createServicePromise).toHaveBeenCalledWith('/api/id', 'DELETE', 'Unable to delete id object.');
        expect(mockScope.message).toBeNull();
        expect(mockScope.error_message).toEqual('Error during delete');
      });
    });
  });
});
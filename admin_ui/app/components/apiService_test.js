'use strict';

describe('addressimoUI.apiService module', function() {

  beforeEach(module('addressimoUI.apiService'));

  describe('GenericAPIService', function() {
    var GenericAPIService, mockHttp, location;

    beforeEach(inject(function (_GenericAPIService_, $httpBackend, $location) {
        GenericAPIService = _GenericAPIService_;
        mockHttp = $httpBackend;
        location = $location;
    }));

    it('tests a GET with 200 return code', function (done) {

        mockHttp.expect('GET', 'http://server:80/api/endpoint', undefined, {'Accept': 'application/json, text/plain, */*'})
            .respond(200, {success: true});

        var promise, promise_generator, response_obj, err_response_obj;

        setTimeout(function () {
            promise_generator = GenericAPIService.createServicePromise('/api/endpoint', 'GET', 'Error Message');
            promise = promise_generator();
            promise.then(
                function (response) {
                    response_obj = response
                },
                function (err) {
                    err_response_obj = err
                }
            );
            mockHttp.flush();

            done();
        }, 100);

        afterEach(function() {
          expect(response_obj).toBeDefined();
          expect(response_obj.iserror).toBeFalsy();
          expect(response_obj.data).toEqual({success: true});

        });

    });

    it('tests a GET with 201 return code', function (done) {

        mockHttp.expect('GET', 'http://server:80/api/endpoint', undefined, {'Accept': 'application/json, text/plain, */*'})
            .respond(201, {success: true});

        var promise, promise_generator, response_obj, err_response_obj;
        setTimeout(function () {
            promise_generator = GenericAPIService.createServicePromise('/api/endpoint', 'GET', 'Error Message');
            promise = promise_generator();
            promise.then(
                function (response) {
                    response_obj = response
                },
                function (err) {
                    err_response_obj = err
                }
            );
            mockHttp.flush();

            done();
        }, 100);

        beforeEach(function () {
            expect(response_obj).toBeDefined();
            expect(response_obj.iserror).toBeFalsy();
            expect(response_obj.data).toEqual({success: true});
        });
    });

    it('tests a GET with 202 return code', function (done) {

        mockHttp.expect('GET', 'http://server:80/api/endpoint', undefined, {'Accept': 'application/json, text/plain, */*'})
            .respond(202, {success: true});

        var promise, promise_generator, response_obj, err_response_obj;
        setTimeout(function () {
            promise_generator = GenericAPIService.createServicePromise('/api/endpoint', 'GET', 'Error Message');
            promise = promise_generator();
            promise.then(
                function (response) {
                    response_obj = response
                },
                function (err) {
                    err_response_obj = err
                }
            );
            mockHttp.flush();

            done();
        }, 100);

        beforeEach(function () {
            expect(response_obj).toBeDefined();
            expect(response_obj.iserror).toBeFalsy();
            expect(response_obj.data).toEqual({success: true});
        });
    });

    it('tests a DELETE with 204 return code', function (done) {

        mockHttp.expect('DELETE', 'http://server:80/api/endpoint', undefined, {'Accept': 'application/json, text/plain, */*'})
            .respond(204, {success: true});

        var promise, promise_generator, response_obj, err_response_obj;

        setTimeout(function () {
            promise_generator = GenericAPIService.createServicePromise('/api/endpoint', 'DELETE', 'Error Message');
            promise = promise_generator();
            promise.then(
                function (response) {
                    response_obj = response
                },
                function (err) {
                    err_response_obj = err
                }
            );
            mockHttp.flush();

            done();
        }, 100);

        beforeEach(function () {
            expect(response_obj).toBeDefined();
            expect(response_obj.iserror).toBeFalsy();
            expect(response_obj.message).toEqual('object deleted');
        });
    });

    it('tests a GET with non-2XX return code', function (done) {

        mockHttp.expect('GET', 'http://server:80/api/endpoint', undefined, {'Accept': 'application/json, text/plain, */*'})
            .respond(400, {success: false, message: 'Error Message'});

        var promise, promise_generator, response_obj, err_response_obj;

        setTimeout(function () {
            promise_generator = GenericAPIService.createServicePromise('/api/endpoint', 'GET', 'Error Message');
            promise = promise_generator();
            promise.then(
                function (response) {
                    response_obj = response
                },
                function (err) {
                    err_response_obj = err
                }
            );
            mockHttp.flush();

            done();
        }, 100);

        beforeEach(function () {
            expect(response_obj).toBeDefined();
            expect(response_obj.iserror).toBeTruthy();
            expect(response_obj.data).toBeUndefined();
            expect(response_obj.message).toEqual('Error Message');
        });
    });

    it('tests a GET with $http throwing an error with generic error message', function (done) {

        mockHttp.expect('GET', 'http://server:80/api/endpoint', undefined, {'Accept': 'application/json, text/plain, */*'})
            .respond(500, {success: false, message: 'Error Message'});

        var promise, promise_generator, response_obj, err_response_obj;

        setTimeout(function () {
            promise_generator = GenericAPIService.createServicePromise('/api/endpoint', 'GET', 'Error Message');
            promise = promise_generator();
            promise.then(
                function (response) {
                    response_obj = response
                },
                function (err) {
                    err_response_obj = err
                }
            );
            mockHttp.flush();

            done();
        }, 100);

        beforeEach(function () {
            expect(response_obj).toBeDefined();
            expect(response_obj.iserror).toBeTruthy();
            expect(response_obj.data).toBeUndefined();
            expect(response_obj.message).toEqual('Error Message');
        });
    });

    it('tests a GET with $http throwing an error with a failures list', function (done) {

        mockHttp.expect('GET', 'http://server:80/api/endpoint', undefined, {'Accept': 'application/json, text/plain, */*'})
            .respond(500, {success: false, message: 'Error Message', failures: [{message: 'Failure Message #1'}]});

        var promise, promise_generator, response_obj, err_response_obj;

        setTimeout(function () {
            promise_generator = GenericAPIService.createServicePromise('/api/endpoint', 'GET', 'Error Message');
            promise = promise_generator();
            promise.then(
                function (response) {
                    response_obj = response
                },
                function (err) {
                    err_response_obj = err
                }
            );
            mockHttp.flush();

            done();
        }, 100);

        beforeEach(function () {
            expect(response_obj).toBeDefined();
            expect(response_obj.iserror).toBeTruthy();
            expect(response_obj.data).toBeUndefined();
            expect(response_obj.message).toEqual('Failure Message #1');
        });
    });

    it('tests a GET with $http throwing an error with no specific error information', function (done) {

        mockHttp.expect('GET', 'http://server:80/api/endpoint', undefined, {'Accept': 'application/json, text/plain, */*'})
            .respond(500, {});

        var promise, promise_generator, response_obj, err_response_obj;

        setTimeout(function () {
            promise_generator = GenericAPIService.createServicePromise('/api/endpoint', 'GET', 'Test Error Message');
            promise = promise_generator();
            promise.then(
                function (response) {
                    response_obj = response
                },
                function (err) {
                    err_response_obj = err
                }
            );
            mockHttp.flush();

            done();
        }, 100);

        beforeEach(function () {
            expect(response_obj).toBeDefined();
            expect(response_obj.iserror).toBeTruthy();
            expect(response_obj.data).toBeUndefined();
            expect(response_obj.message).toEqual('Test Error Message');
        });
    });

    it('tests a POST with 201 return code', function (done) {

        mockHttp.expect('POST', 'http://server:80/api/endpoint', {something: 'this thing'}, {'Content-Type': 'application/json', 'Accept': 'application/json, text/plain, */*'})
            .respond(201, {success: true, domains: ['test.com']});

        var promise, promise_generator, response_obj, err_response_obj;

        setTimeout(function () {
            promise_generator = GenericAPIService.createServicePromise('/api/endpoint', 'POST', 'Test Error Message');
            promise = promise_generator({something: 'this thing'});
            promise.then(
                function (response) {
                    response_obj = response
                },
                function (err) {
                    err_response_obj = err
                }
            );
            mockHttp.flush();

            done();
        }, 100);

        beforeEach(function () {
            expect(response_obj).toBeDefined();
            expect(response_obj.iserror).toBeFalsy();
            expect(response_obj.data).toEqual({success: true, domains: ['test.com']});
        });
    });
  });
});
'use strict';

var app = angular.module('torrentSearcher', [
		// Angular Libraries.
		'ngRoute', 'ngAnimate', 'ngResource', 'ngSanitize',

		// App.
		'torrentSearcher',

		// External Libs.
		'ui.bootstrap', 'ui.router', 'ui.utils'
	]);

app.controller('torrentTable', ['$scope','$http', function($scope,$http) {
    $http.get('test/test.json').success(function(data) {
        $scope.results = data;
    });
}]);
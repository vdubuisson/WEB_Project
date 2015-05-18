var app = angular.module('web', []);

app.controller('WebCtrl', function($scope, $http){
	$http.post('http://localhost:5000/', "").success(function(data, status) {
		$scope.rubriques = data;
		
	}).error(function(data){
	});
});



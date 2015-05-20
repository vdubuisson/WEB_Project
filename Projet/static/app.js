var app = angular.module('web', []);

app.controller('Accueil', function($scope, $http){
	$http.post('http://localhost:5000/', "").success(function(data, status) {
		$scope.bienvenue = data[0];
		data.shift();
		$scope.rubriques = data;
		
				
	}).error(function(data){
	});
});

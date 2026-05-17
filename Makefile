.PHONY: deploy clean

deploy:
	kubectl apply -f k8s/01-secret.yaml
	kubectl apply -f k8s/02-configmap.yaml
	kubectl apply -f k8s/03-pvc.yaml
	kubectl apply -f k8s/04-init-sql.yaml
	kubectl apply -f k8s/05-postgres.yaml
	kubectl apply -f k8s/06-postgres-svc.yaml
	kubectl wait --for=condition=Ready pod/postgres --timeout=120s
	kubectl apply -f k8s/07-backend-deployment.yaml
	kubectl apply -f k8s/08-backend-svc.yaml
	kubectl apply -f k8s/09-hpa.yaml
	kubectl wait --for=condition=Available deployment/backend --timeout=120s
	kubectl apply -f k8s/10-frontend-html.yaml
	kubectl apply -f k8s/11-frontend-deployment.yaml
	kubectl apply -f k8s/12-frontend-svc.yaml
	kubectl wait --for=condition=Available deployment/frontend --timeout=60s
	@echo "Desplegado. Usa: kubectl port-forward svc/backend-service 5000:80"
	@echo "y en otra terminal: kubectl port-forward svc/frontend-service 8080:80"

clean:
	kubectl delete -f k8s/12-frontend-svc.yaml --ignore-not-found
	kubectl delete -f k8s/11-frontend-deployment.yaml --ignore-not-found
	kubectl delete -f k8s/10-frontend-html.yaml --ignore-not-found
	kubectl delete -f k8s/09-hpa.yaml --ignore-not-found
	kubectl delete -f k8s/08-backend-svc.yaml --ignore-not-found
	kubectl delete -f k8s/07-backend-deployment.yaml --ignore-not-found
	kubectl delete -f k8s/06-postgres-svc.yaml --ignore-not-found
	kubectl delete -f k8s/05-postgres.yaml --ignore-not-found
	kubectl delete -f k8s/04-init-sql.yaml --ignore-not-found
	# PVC NO se borra para conservar datos
	kubectl delete -f k8s/02-configmap.yaml --ignore-not-found
	kubectl delete -f k8s/01-secret.yaml --ignore-not-found
	@echo "Limpieza completada."
targetScope = 'resourceGroup'

@description('Azure region for FactoryVision resources.')
param location string = 'westeurope'

@description('Display-form Azure region used by Cosmos DB account locations.')
param cosmosLocationName string = 'West Europe'

@description('Static Web App resource name.')
param staticWebAppName string = 'factoryvision-web'

@description('Cosmos DB account name. Must be globally unique.')
param cosmosAccountName string = 'factoryvision-${uniqueString(subscription().subscriptionId, resourceGroup().id)}'

@description('Container Apps environment name.')
param containerEnvironmentName string = 'factoryvision-env'

@description('Container App name.')
param containerAppName string = 'factoryvision-api'

@description('Public GHCR image that contains the verified PatchCore release.')
param containerImage string = 'ghcr.io/chaima-menouar/factoryvision-ai:azure-latest'

@description('Create the Container Apps backend only after the GHCR image is available.')
param deployBackend bool = false

@description('Maximum number of persisted inspections accepted per UTC day.')
@minValue(1)
@maxValue(100)
param dailyInspectionLimit int = 25

@description('Maximum image upload size in bytes.')
@minValue(1048576)
@maxValue(10485760)
param maxUploadBytes int = 6291456

var tags = {
  project: 'FactoryVision-AI'
  workload: 'portfolio-demo'
  costPolicy: 'zero-cost-first'
}

resource staticWebApp 'Microsoft.Web/staticSites@2025-03-01' = {
  name: staticWebAppName
  location: location
  tags: tags
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {}
}

resource cosmos 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' = {
  name: cosmosAccountName
  location: location
  tags: tags
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    enableFreeTier: true
    enableAutomaticFailover: false
    enableMultipleWriteLocations: false
    enableAnalyticalStorage: false
    publicNetworkAccess: 'Enabled'
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    locations: [
      {
        locationName: cosmosLocationName
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
  }
}

resource database 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2024-05-15' = {
  parent: cosmos
  name: 'factoryvision'
  properties: {
    resource: {
      id: 'factoryvision'
    }
    options: {
      throughput: 400
    }
  }
}

resource inspections 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-05-15' = {
  parent: database
  name: 'inspections'
  properties: {
    resource: {
      id: 'inspections'
      partitionKey: {
        paths: [
          '/id'
        ]
        kind: 'Hash'
        version: 2
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        automatic: true
        includedPaths: [
          {
            path: '/*'
          }
        ]
        excludedPaths: [
          {
            path: '/"_etag"/?'
          }
        ]
      }
    }
    options: {}
  }
}

resource environment 'Microsoft.App/managedEnvironments@2026-01-01' = if (deployBackend) {
  name: containerEnvironmentName
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'none'
    }
  }
}

resource api 'Microsoft.App/containerApps@2026-01-01' = if (deployBackend) {
  name: containerAppName
  location: location
  tags: tags
  properties: {
    managedEnvironmentId: environment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8000
        allowInsecure: false
        transport: 'auto'
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
      secrets: [
        {
          name: 'cosmos-key'
          value: cosmos.listKeys().primaryMasterKey
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'factoryvision-api'
          image: containerImage
          resources: {
            cpu: json('2.0')
            memory: '4Gi'
          }
          env: [
            {
              name: 'FACTORYVISION_MODEL_CHECKPOINT'
              value: '/app/artifacts/model.ckpt'
            }
            {
              name: 'FACTORYVISION_DB_BACKEND'
              value: 'cosmos'
            }
            {
              name: 'FACTORYVISION_COSMOS_ENDPOINT'
              value: cosmos.properties.documentEndpoint
            }
            {
              name: 'FACTORYVISION_COSMOS_KEY'
              secretRef: 'cosmos-key'
            }
            {
              name: 'FACTORYVISION_COSMOS_DATABASE'
              value: 'factoryvision'
            }
            {
              name: 'FACTORYVISION_COSMOS_CONTAINER'
              value: 'inspections'
            }
            {
              name: 'FACTORYVISION_CORS_ORIGINS'
              value: 'https://${staticWebApp.properties.defaultHostname}'
            }
            {
              name: 'FACTORYVISION_COPILOT_PROVIDER'
              value: 'disabled'
            }
            {
              name: 'FACTORYVISION_DAILY_INSPECTION_LIMIT'
              value: string(dailyInspectionLimit)
            }
            {
              name: 'FACTORYVISION_MAX_UPLOAD_BYTES'
              value: string(maxUploadBytes)
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 1
        rules: [
          {
            name: 'http'
            http: {
              metadata: {
                concurrentRequests: '1'
              }
            }
          }
        ]
      }
    }
  }
}

output staticWebAppHostname string = staticWebApp.properties.defaultHostname
output cosmosEndpoint string = cosmos.properties.documentEndpoint
output backendEnabled bool = deployBackend
output backendHostname string = deployBackend ? api.properties.configuration.ingress.fqdn : ''

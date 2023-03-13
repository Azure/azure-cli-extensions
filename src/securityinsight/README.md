# Azure CLI Sentinel Extension #
This is an extension to Azure CLI to manage sentinel resources.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name sentinel
```

### Included Features ###
#### sentinel alert-rule ####
##### Create #####
```
az sentinel alert-rule create -n myRule -w myWorkspace -g myRG \
    --ms-security-incident "{product-filter:'Microsoft Cloud App Security',display-name:testing,enabled:true}"
```
##### List #####
```
az sentinel alert-rule list -w myWorkspace -g myRG
```
##### Update #####
```
az sentinel alert-rule update -n myRule -w myWorkspace -g myRG \
    --ms-security-incident display-name=tested
```
##### Show #####
```
az sentinel alert-rule show -n myRule -w myWorkspace -g myRG
```
##### Delete #####
```
az sentinel alert-rule delete -n myRule -w myWorkspace -g myRG --yes
```

#### sentinel alert-rule template ####
##### List #####
```
az sentinel alert-rule template list -w myWorkspace -g myRG
```
##### Show #####
```
az sentinel alert-rule template show -n myTemplate -w myWorkspace -g myRG
```

#### sentinel automation-rule ####
##### Create #####
```
az sentinel automation-rule create -n myRule -w myWorkspace -g myRG \
    --display-name 'High severity incidents escalation' --order 1 \
    --actions "[{order:1,modify-properties:{action-configuration:{severity:High}}}]" \
    --triggering-logic "{is-enabled:true,triggers-on:Incidents,triggers-when:Created}"
```
##### List #####
```
az sentinel automation-rule list -w myWorkspace -g myRG
```
##### Update #####
```
az sentinel automation-rule update -n myRule -w myWorkspace -g myRG \
    --display-name 'New name'
```
##### Show #####
```
az sentinel automation-rule show -n myRule -w myWorkspace -g myRG
```
##### Delete #####
```
az sentinel automation-rule delete -n myRule -w myWorkspace -g myRG --yes
```

#### sentinel bookmark ####
##### Create #####
```
az sentinel bookmark create -n myBookmark -w myWorkspace -g myRG \
    --query-content 'SecurityEvent | where TimeGenerated > ago(1d) and TimeGenerated < ago(2d)' \
    --query-result 'Security Event query result' --display-name 'My bookmark' --notes 'Found a suspicious activity' \
    --entity-mappings "[{entity-type:Account,field-mappings:[{identifier:Fullname,value:johndoe@microsoft.com}]}]" \
    --tactics "[Execution]" --techniques "[T1609]" --labels "[Tag1,Tag2]"
```
##### List #####
```
az sentinel bookmark list -w myWorkspace -g myRG
```
##### Show #####
```
az sentinel bookmark show -n myBookmark -w myWorkspace -g myRG
```
##### Delete #####
```
az sentinel bookmark delete -n myBookmark -w myWorkspace -g myRG --yes
```

#### sentinel bookmark relation ####
##### Create #####
```
az sentinel bookmark relation create -n myRelation -w myWorkspace -g myRG \
    --bookmark-id myBookmark --related-resource-id myIncident
```
##### List #####
```
az sentinel bookmark relation list -w myWorkspace -g myRG \
    --bookmark-id myBookmark
```
##### Show #####
```
az sentinel bookmark relation show -n myRelation -w myWorkspace -g myRG \
    --bookmark-id myBookmark
```
##### Delete #####
```
az sentinel bookmark relation delete -n myRelation -w myWorkspace -g myRG \
    --bookmark-id myBookmark --yes
```

#### sentinel incident ####
##### Create #####
```
az sentinel incident create -n myIncident -w myWorkspace -g myRG \
    --classification FalsePositive --classification-reason IncorrectAlertLogic \
    --classification-comment 'Not a malicious activity' --first-activity-time-utc 2019-01-01T13:00:30Z \
    --last-activity-time-utc 2019-01-01T13:05:30Z --severity High --status Closed --title 'My incident' \
    --description 'This is a demo incident' \
    --owner "{object-id:2046feea-040d-4a46-9e2b-91c2941bfa70}"
```
##### List #####
```
az sentinel incident list -w myWorkspace -g myRG --orderby 'properties/createdTimeUtc desc' --top 1
```
##### Show #####
```
az sentinel incident show -n myIncident -w myWorkspace -g myRG
```
##### Delete #####
```
az sentinel incident delete -n myIncident -w myWorkspace -g myRG --yes
```

#### sentinel incident relation ####
##### Create #####
```
az sentinel incident relation create -n myRelation -w myWorkspace -g myRG \
    --incident-id myIncident --related-resource-id myBookmark
```
##### List #####
```
az sentinel incident relation list -w myWorkspace -g myRG \
    --incident-id myIncident
```
##### Show #####
```
az sentinel incident relation show -n myRelation -w myWorkspace -g myRG \
    --incident-id myIncident
```
##### Delete #####
```
az sentinel incident relation delete -n myRelation -w myWorkspace -g myRG \
    --incident-id myIncident --yes
```

#### sentinel incident comment ####
##### Create #####
```
az sentinel incident comment create -n myComment -w myWorkspace -g myRG \
    --incident-id myIncident --message 'Some message'
```
##### List #####
```
az sentinel incident comment list -w myWorkspace -g myRG \
    --incident-id myIncident
```
##### Update #####
```
az sentinel incident comment update -n myComment -w myWorkspace -g myRG \
    --incident-id myIncident --message 'Some messages'
```
##### Show #####
```
az sentinel incident comment show -n myComment -w myWorkspace -g myRG \
    --incident-id myIncident
```
##### Delete #####
```
az sentinel incident comment delete -n myComment -w myWorkspace -g myRG \
    --incident-id myIncident --yes
```

#### sentinel enrichment domain-whois ####
##### Show #####
```
az sentinel enrichment domain-whois show -g myRG --domain microsoft.com
```

#### sentinel enrichment ip-geodata ####
##### Show #####
```
az sentinel enrichment ip-geodata show -g myRG --ip-address 1.2.3.4
```

#### sentinel metadata ####
##### Create #####
```
az sentinel metadata create -n myMetadata -w myWorkspace -g myRG \
    --content-id myContent --parent-id myRule --kind AnalyticsRule
```
##### List #####
```
az sentinel metadata list -w myWorkspace -g myRG
```
##### Update #####
```
az sentinel metadata update -n myMetadata -w myWorkspace -g myRG \
    --author "{name:cli,email:cli@microsoft.com}"
```
##### Show #####
```
az sentinel metadata show -n myMetadata -w myWorkspace -g myRG
```
##### Delete #####
```
az sentinel metadata delete -n myMetadata -w myWorkspace -g myRG --yes
```

#### sentinel onboarding-state ####
##### Create #####
```
az sentinel onboarding-state create -n defalut -w myWorkspace -g myRG \
    --customer-managed-key false
```
##### List #####
```
az sentinel onboarding-state list -w myWorkspace -g myRG
```
##### Show #####
```
az sentinel onboarding-state show -n defalut -w myWorkspace -g myRG
```
##### Delete #####
```
az sentinel onboarding-state delete -n defalut -w myWorkspace -g myRG --yes
```

#### sentinel threat-indicator ####
##### Create #####
```
az sentinel threat-indicator create -w myWorkspace -g myRG \
    --source 'Microsoft Sentinel' --display-name 'new schema' --confidence 78 --created-by-ref contoso@contoso.com \
    --modified '' --pattern '[url:value = 'https://www.contoso.com']' --pattern-type url --revoked false \
    --valid-from 2022-06-15T17:44:00.114052Z --valid-until '' --description 'debugging indicators' \
    --threat-tags "['new schema']" --threat-types "[compromised]" --external-references "[]"
```
##### List #####
```
az sentinel threat-indicator list -w myWorkspace -g myRG
```
##### Show #####
```
az sentinel threat-indicator show -n myIndictor -w myWorkspace -g myRG
```
##### Delete #####
```
az sentinel threat-indicator delete -n myIndictor -w myWorkspace -g myRG --yes
```

#### sentinel watchlist ####
##### Create #####
```
az sentinel watchlist create -n myWatchlist -w myWorkspace -g myRG \
    --description 'Watchlist from CSV content' --display-name 'High Value Assets Watchlist'
    --provider Microsoft --items-search-key header1
```
##### List #####
```
az sentinel watchlist list -w myWorkspace -g myRG
```
##### Update #####
```
az sentinel watchlist update -n myWatchlist -w myWorkspace -g myRG \
    --display-name 'New name'
```
##### Show #####
```
az sentinel watchlist show -n myWatchlist -w myWorkspace -g myRG
```
##### Delete #####
```
az sentinel watchlist delete -n myWatchlist -w myWorkspace -g myRG --yes
```

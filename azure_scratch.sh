#!/bin/bash
SCOPE=/subscriptions/55093e67-09be-455b-bee4-802b5ba38768/resourceGroups/ip5-scggov
# az policy assignment list --scope $SCOPE  --disable-scope-strict-match
INITIATIVES=$(az policy assignment list \
  --scope $SCOPE \
  --disable-scope-strict-match \
  --query "[?policyDefinitionId.contains(@, 'policySetDefinitions')].policyDefinitionId" \
  --output tsv)

# Step 2: Loop through each initiative and check if it includes the specific policy definition
TARGET_POLICY_ID="/providers/Microsoft.Authorization/policyDefinitions/df49d893-a74c-421d-bc95-c663042e5b80"
echo "Searching for policy ID: $TARGET_POLICY_ID in assigned initiatives..."

for initiative_id in $INITIATIVES; do
  INITIATIVE_NAME=$(basename "$initiative_id")
  MATCH=$(az policy set-definition show --name "$INITIATIVE_NAME" \
    --query "policyDefinitions[?policyDefinitionId=='$TARGET_POLICY_ID']" \
    --output tsv)

  if [[ -n "$MATCH" ]]; then
    echo "✅ Found in initiative: $INITIATIVE_NAME ($initiative_id)"
  else
    echo "⛔ Not in initiative: $INITIATIVE_NAME"
  fi
done

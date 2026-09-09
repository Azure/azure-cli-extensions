Do these updates after you export new code from the AAZDev tool:

- Update api-version from 2026-09-15-preview to 2026-07-15-preview everywhere, since the service does not use support 9-15
- Update _create.py to add example:
    ```python
    class Create(AAZCommand):
        """Create a cost control.

        :example: Create a monthly cost control for an agent
            az cognitive-services account cost-control create --resource-group MyResourceGroup --account-name MyAccount --cost-control-name MyCostControl --display-name "Display Name" --rules '[{"name":"per-agent-monthly","counterKey":[{"type":"agent"}],"unit":"usd","amount":200,"period":"month","recurring":true,"match":{"foundryCallerAgentId":["agent-123"]},"thresholds":[{"type":"percentage","value":80,"action":"alert"},{"type":"absolute","value":200,"action":"audit"}]}]'
        """
    ```
- Update _update.py to add example:
    ```python
    class Update(AAZCommand):
        """Update a cost control.

        :example: Update the display name of a cost control
            az cognitive-services account cost-control update --resource-group MyResourceGroup --account-name MyAccount --cost-control-name MyCostControl --display-name "Updated Display Name"
        """
    ```



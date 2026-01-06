<!-- All of Project saved in GitHub -->
DaC Component:
    - Rule Base (Base Use Sigma + ELK Sec Rule):
        + SIEM Type:
            Device Type:
                - Base Rule:
                    Base Rule of Device
                - Vendor:
                    Speacial Rule for Vendor
    - Rule of Tenant:
        + Each Tenant => Tenant Config (logsource,...) + Tenant Rule
    - Log Requirement:
        + Device => Vendor => LogSource => LogSourceMapping Base
    - Test Case (Idea)
    - Management Tool:
        + View/List/...
        + Auto Merge Tool
    - Rule Management UI (web - idea)

Rule Base Format:
    - Logic Sigma rule
    - Custom Field:
        + SIEM Rule
        + SIEM Config for Auto Deployment

Demo how DaC work:
    <!-- Prepare for Auto Merge -->
    - Automation Deployment:
        Requirement: LogSource + FieldMapping
        WorkFlow:
        LogSource ==(Collect Rule Tool)==> Rule Base ==(Processing Tool + FieldMapping.json)==> Rule Base of Tenant ==(Processing Tool)==> Rule Pre-Deployment ==(Automation Deployment Tool)==> Rule in Customer SIEM
    - Rule Management:
        + View/List Rule:
            Phase 1: Using Python/Golang to View/List + Integrate into modules for use by others.
            Phase 2: Create Web Base, interact by UI
        + Tuning Rule:
            Reviece Tuning Request via form (We're temporarily using the form from the old management system, and will integrate it into RuleManagerWeb in the future.) => Memember process request => New Tuned Rule ==(Auto Merge Rule Tool)==> Rule Tuned in Customer Site + Rule Merge to Git 
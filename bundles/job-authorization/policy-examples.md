---
type: Reference
title: IAM policy examples and review rules
description: Illustrative runner, broker, target-role and per-run policies for the selected architecture.
status: draft
generated: {by: codex/gpt-6, at: "2026-09-24T00:23:59+02:00"}
sources:
  - id: trust
    resource: https://docs.aws.amazon.com/rolesanywhere/latest/userguide/trust-model.html
  - id: variables
    resource: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_variables.html
  - id: sts
    resource: https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html
---
# IAM policy examples and review rules

Examples are syntactically valid JSON, not a complete deployable stack. Replace account IDs, organization, region, API ID, anchor ID, role ARNs and resource names. Validate with IAM Access Analyzer and live positive/negative tests. Attached SCPs, boundaries, endpoint policies, key policies and resource policies must be reviewed together.

## 1. Common runner trust policy

Attach to `OnPremRunnerProd` in `111111111111`. The trust admits the Roles Anywhere service through a specific anchor and approved certificate attributes. Roles Anywhere requires AssumeRole, TagSession and SetSourceIdentity trust permissions.[^trust]

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "OnlyApprovedRunnerCertificates",
    "Effect": "Allow",
    "Principal": {"Service": "rolesanywhere.amazonaws.com"},
    "Action": ["sts:AssumeRole", "sts:TagSession", "sts:SetSourceIdentity"],
    "Condition": {
      "ArnEquals": {"aws:SourceArn": "arn:aws:rolesanywhere:eu-central-1:111111111111:trust-anchor/EXAMPLE_ANCHOR_ID"},
      "StringEquals": {
        "aws:SourceAccount": "111111111111",
        "aws:PrincipalTag/x509Subject/OU": "batch-prod"
      },
      "StringLike": {"aws:PrincipalTag/x509Subject/CN": "n-*"},
      "Null": {"aws:PrincipalTag/x509Subject/CN": "false"}
    }
  }]
}
```

The registration service enforces the full NodeId grammar; `n-*` alone does not. Configure the profile with only this role, 900-second sessions and `acceptRoleSessionName=false`. Explicitly preserve the CN and OU mappings. Do not rely solely on profiles as the role trust boundary: protect the role independently of other profiles administrators might create.

## 2. Common runner permissions

Attach only the following business-access policy to the runner. The role's certificate-derived CN binds the method path. Resource variables are an IAM feature; the path construction remains a design that needs integration tests.[^variables]

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "InvokeOwnNodeCredentialMethod",
      "Effect": "Allow",
      "Action": "execute-api:Invoke",
      "Resource": "arn:aws:execute-api:eu-central-1:111111111111:EXAMPLE_API_ID/prod/POST/nodes/${aws:PrincipalTag/x509Subject/CN}/credentials"
    },
    {
      "Sid": "DenyOtherInvocationPaths",
      "Effect": "Deny",
      "Action": "execute-api:Invoke",
      "NotResource": "arn:aws:execute-api:eu-central-1:111111111111:EXAMPLE_API_ID/prod/POST/nodes/${aws:PrincipalTag/x509Subject/CN}/credentials"
    },
    {
      "Sid": "DenyMissingNodeIdentity",
      "Effect": "Deny",
      "Action": "execute-api:Invoke",
      "Resource": "*",
      "Condition": {"Null": {"aws:PrincipalTag/x509Subject/CN": "true"}}
    },
    {
      "Sid": "RunnerHasNoOtherBusinessCapabilities",
      "Effect": "Deny",
      "NotAction": "execute-api:Invoke",
      "Resource": "*"
    }
  ]
}
```

That broad explicit deny intentionally prevents the runner from calling STS, S3, Private CA and other business APIs. Renewal uses its separate enrollment protocol. Diagnostic behavior of APIs such as GetCallerIdentity should not be treated as a data-access grant. The private API must enforce AWS_IAM and network restrictions, with no alternate route to the integration.

## 3. Broker permission to assume a target job role

This is the broker's target-access statement. Add separately scoped logging/registry/runtime permissions needed by its implementation. Only the broker runtime receives this policy. Lambda's service trust must not admit the on-prem runner.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "AssumeProductAJobA",
    "Effect": "Allow",
    "Action": ["sts:AssumeRole", "sts:TagSession", "sts:SetSourceIdentity"],
    "Resource": "arn:aws:iam::222222222222:role/product/product-a/prod/job-a",
    "Condition": {
      "StringEquals": {
        "aws:RequestTag/ProductId": "product-a",
        "aws:RequestTag/Environment": "prod",
        "aws:RequestTag/JobId": "job-a"
      }
    }
  }]
}
```

Use one explicit statement per approved capability. Do not use `arn:aws:iam::*:role/*` or let job input construct the ARN. This policy prevents accidental role expansion, but a compromised broker can still invoke any capability assigned to it.

## 4. Target trust policy

Attach to `product/product-a/prod/job-a` in account `222222222222`.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "OnlyApprovedBrokerAndJobClass",
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::111111111111:role/CredentialBrokerProd"},
    "Action": ["sts:AssumeRole", "sts:TagSession", "sts:SetSourceIdentity"],
    "Condition": {
      "StringEquals": {
        "aws:PrincipalOrgID": "o-exampleorg",
        "aws:RequestTag/ProductId": "product-a",
        "aws:RequestTag/Environment": "prod",
        "aws:RequestTag/JobId": "job-a"
      },
      "StringLike": {
        "aws:RequestTag/RunId": "r-*",
        "aws:RequestTag/NodeId": "n-*",
        "sts:RoleSessionName": "product-a-*",
        "sts:SourceIdentity": "run-r-*"
      },
      "ForAllValues:StringEquals": {
        "aws:TagKeys": ["ProductId", "Environment", "JobId", "RunId", "NodeId"]
      },
      "Null": {
        "aws:RequestTag/ProductId": "false",
        "aws:RequestTag/Environment": "false",
        "aws:RequestTag/JobId": "false",
        "aws:RequestTag/RunId": "false",
        "aws:RequestTag/NodeId": "false",
        "sts:SourceIdentity": "false",
        "sts:TransitiveTagKeys": "true"
      }
    }
  }]
}
```

The IAM conditions validate presence, allowed keys and coarse shape. They do not prove the job is running or that RunId matches a real scheduler run; that is the broker's duty. No `IfExists` exemption is used for mandatory authorization claims. The baseline disallows transitive-tag requests and subsequent role chaining by jobs.

## 5. Target job-class permission policy

This S3-only example uses unencrypted-by-customer-key objects for policy clarity; add exact KMS permissions and key-policy controls when SSE-KMS is used. It intentionally omits bucket listing; the job receives known object keys.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadJobAInputs",
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::corp-product-a-prod-example/job-a/input/*"
    },
    {
      "Sid": "WriteJobAOutputs",
      "Effect": "Allow",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::corp-product-a-prod-example/job-a/output/*"
    },
    {
      "Sid": "DenyPrivilegeDelegation",
      "Effect": "Deny",
      "Action": ["sts:AssumeRole", "iam:*", "organizations:*", "acm-pca:*"],
      "Resource": "*"
    }
  ]
}
```

## 6. Broker-generated run session policy

For `r-01abc`, assume input staging has copied the approved data to the run input prefix. Session policies narrow identity permissions and are subject to STS size/packing limits.[^sts] The deny statements below prevent grants for these S3 actions outside the run prefixes from bypassing the intended confinement.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::corp-product-a-prod-example/job-a/input/r-01abc/*"
    },
    {
      "Effect": "Allow",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::corp-product-a-prod-example/job-a/output/r-01abc/*"
    },
    {
      "Effect": "Deny",
      "Action": "s3:GetObject",
      "NotResource": "arn:aws:s3:::corp-product-a-prod-example/job-a/input/r-01abc/*"
    },
    {
      "Effect": "Deny",
      "Action": "s3:PutObject",
      "NotResource": "arn:aws:s3:::corp-product-a-prod-example/job-a/output/r-01abc/*"
    },
    {
      "Effect": "Deny",
      "NotAction": ["s3:GetObject", "s3:PutObject"],
      "Resource": "*"
    }
  ]
}
```

This strict session policy also denies KMS, listing, versioned reads and multipart helper actions. Add required operations explicitly in both baseline and session scope after review; otherwise SDK transfers may fail. Do not “fix” failures by removing denies wholesale. The broker sends compact JSON and monitors `PackedPolicySize`.

## Policy review rules

- Prevent direct resource-policy grants to arbitrary assumed-role session ARNs and ungoverned product tags.
- Grant target-role administration only through reviewed IaC; detect changes to trust, permissions and boundaries.
- Use SCPs to restrict unauthorized IAM/CA/Organizations administration; SCPs do not grant permissions.
- Treat source identity as immutable during an existing chain. This architecture starts the job session from the broker's independent runtime session, which must have no incompatible preexisting source identity.
- Run the full [negative-test matrix](../operations/acceptance-tests.md), particularly other NodeId paths, missing mappings, omitted policies and cross-product resources.

[^trust]: [Roles Anywhere trust permissions](https://docs.aws.amazon.com/rolesanywhere/latest/userguide/trust-model.html).
[^variables]: [IAM resource variables](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_variables.html).
[^sts]: [STS AssumeRole policies and limits](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html).

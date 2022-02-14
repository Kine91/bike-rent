import pulumi
import pulumi_aws as aws
import json
from pulumi import Output

ENV = pulumi.get_stack().split("-")[-1]

def public_read_policy_for_bucket(values):
    return json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": values[1]},
                    "Action": ["s3:GetObject"],
                    "Resource": [
                        f"arn:aws:s3:::{values[0]}/*",
                    ],
                }
            ],
        }
    )


origin_access_identity = aws.cloudfront.OriginAccessIdentity(
    f"bike-rent-front-access-identity-{ENV}",
    comment=f"bike-rent-front-access-identity-{ENV}",
)

bucket = aws.s3.Bucket(
    f"bike-rent-web-content-{ENV}",
    force_destroy=True,
    acl="private",
    website={
        "index_document": "index.html",
    })

pulumi.export('front_bucket',  bucket.id)

root_bucket_policy = aws.s3.BucketPolicy(
    f"bike-rent-bucket-policy-{ENV}",
    bucket=bucket.id,
    policy=Output.all(bucket.id, origin_access_identity.iam_arn).apply(
        public_read_policy_for_bucket
    ),
)

s3_origin_id = "bike-rent-front"


s3_distribution = aws.cloudfront.Distribution(
    "s3Distribution",
    origins=[aws.cloudfront.DistributionOriginArgs(
        domain_name=bucket.bucket_regional_domain_name,
        origin_id=s3_origin_id,
        s3_origin_config=aws.cloudfront.DistributionOriginS3OriginConfigArgs(
            origin_access_identity=origin_access_identity.cloudfront_access_identity_path
        ),
    )],
    enabled=True,
    is_ipv6_enabled=True,
    comment="Bike Rent CloudFront",
    default_root_object="index.html",
    # logging_config=aws.cloudfront.DistributionLoggingConfigArgs(
    #     include_cookies=False,
    #     bucket="mylogs.s3.amazonaws.com",
    #     prefix="myprefix",
    # ),
    # aliases=[
    #     "mysite.example.com",
    #     "yoursite.example.com",
    # ],
    default_cache_behavior=aws.cloudfront.DistributionDefaultCacheBehaviorArgs(
        allowed_methods=["DELETE", "GET", "HEAD",
                         "OPTIONS", "PATCH", "POST", "PUT"],
        cached_methods=["GET", "HEAD"],
        target_origin_id=s3_origin_id,
        forwarded_values=aws.cloudfront.DistributionDefaultCacheBehaviorForwardedValuesArgs(
            query_string=True,
            cookies=aws.cloudfront.DistributionDefaultCacheBehaviorForwardedValuesCookiesArgs(
                forward="none",
            ),
        ),
        viewer_protocol_policy="redirect-to-https",
        min_ttl=0,
        default_ttl=3600,
        max_ttl=86400,
    ),
    # ordered_cache_behaviors=[
    #     aws.cloudfront.DistributionOrderedCacheBehaviorArgs(
    #         path_pattern="/content/immutable/*",
    #         allowed_methods=[
    #             "GET",
    #             "HEAD",
    #             "OPTIONS",
    #         ],
    #         cached_methods=[
    #             "GET",
    #             "HEAD",
    #             "OPTIONS",
    #         ],
    #         target_origin_id=s3_origin_id,
    #         forwarded_values=aws.cloudfront.DistributionOrderedCacheBehaviorForwardedValuesArgs(
    #             query_string=False,
    #             headers=["Origin"],
    #             cookies=aws.cloudfront.DistributionOrderedCacheBehaviorForwardedValuesCookiesArgs(
    #                 forward="none",
    #             ),
    #         ),
    #         min_ttl=0,
    #         default_ttl=86400,
    #         max_ttl=31536000,
    #         compress=True,
    #         viewer_protocol_policy="redirect-to-https",
    #     ),
    #     aws.cloudfront.DistributionOrderedCacheBehaviorArgs(
    #         path_pattern="/content/*",
    #         allowed_methods=[
    #             "GET",
    #             "HEAD",
    #             "OPTIONS",
    #         ],
    #         cached_methods=[
    #             "GET",
    #             "HEAD",
    #         ],
    #         target_origin_id=s3_origin_id,
    #         forwarded_values=aws.cloudfront.DistributionOrderedCacheBehaviorForwardedValuesArgs(
    #             query_string=False,
    #             cookies=aws.cloudfront.DistributionOrderedCacheBehaviorForwardedValuesCookiesArgs(
    #                 forward="none",
    #             ),
    #         ),
    #         min_ttl=0,
    #         default_ttl=3600,
    #         max_ttl=86400,
    #         compress=True,
    #         viewer_protocol_policy="redirect-to-https",
    #     ),
    # ],
    price_class="PriceClass_100",
    restrictions=aws.cloudfront.DistributionRestrictionsArgs(
        geo_restriction=aws.cloudfront.DistributionRestrictionsGeoRestrictionArgs(
            restriction_type="none",
        )
    ),
    tags={
        "Environment": "production",
    },
    viewer_certificate=aws.cloudfront.DistributionViewerCertificateArgs(
        cloudfront_default_certificate=True,
    ))

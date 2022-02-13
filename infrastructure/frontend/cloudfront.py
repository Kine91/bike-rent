import pulumi
import pulumi_aws as aws

bucket = aws.s3.Bucket(
    "bike-rent-web-content",
    force_destroy=True,
    acl="private",
    website={
        "index_document": "index.html",
    })

s3_origin_id = "bike-rent-front"

origin_access_identity = aws.cloudfront.OriginAccessIdentity(
    f"bike-rent-front-access-identity",
    comment=f"bike-rent-front-access-identity",
)

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

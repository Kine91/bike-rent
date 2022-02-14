import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as mime from "mime";
import * as utils from "./utils";

const stackName = pulumi.getStack();
const env = stackName.split("-").pop();

const infraStackName = `bike-rent-front-infra-${env}`;
const stack = new pulumi.StackReference(infraStackName);

// const apiStackName = `resource-manager-data-layer-${env}`;
// const apiStack = new pulumi.StackReference(apiStackName);

const siteDir = "./../build";
const buildFiles = utils.getAllFiles(siteDir, []);

const outputRoot = stack
  .getOutput("front_bucket")
  .apply((value: string) => value);

pulumi.all([outputRoot]).apply(([rootAppBucket]) => {
  if (!rootAppBucket) {
    console.error("No bucket name!");
    return;
  }

  for (let filePath of buildFiles) {
    const fileName = filePath.split("/").pop() as string;

    const fileKey = filePath
      .substring(filePath.indexOf("/build/"))
      .replace("/build/", ``);

    if (fileName !== ".gitkeep") {
      new aws.s3.BucketObject(fileName, {
        bucket: rootAppBucket,
        key: fileKey,
        forceDestroy: true,
        source: new pulumi.asset.FileAsset(filePath), // use FileAsset to point to a file
        contentType: mime.getType(filePath) || undefined, // set the MIME type of the file
      });
    }
  }
});

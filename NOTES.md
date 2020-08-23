
### Set up CodePipeline for pushing the image to an ECR

Set up a service role:
https://docs.aws.amazon.com/codebuild/latest/userguide/setting-up.html#setting-up-service-role (Section "Create a CodeBuild service role")

Be sure to add the additional policy "AmazonEC2ContainerRegistryPowerUser" to the role.

Set up CodePipeline:
https://aws.amazon.com/de/blogs/devops/build-a-continuous-delivery-pipeline-for-your-container-images-with-amazon-ecr-as-source/ (Section "Create a continuous deployment pipeline")

In contrast to this tutorial:
- Set the CloudBuild runtime to "Standard", not "Docker" and use the latest version
- Privileged access must be activated in the CloudBuild build
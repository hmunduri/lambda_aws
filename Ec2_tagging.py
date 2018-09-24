import os
import re
import json
import boto3

"""
@author Himagiri Munduri
Tagging of ELBs missing the tags from the associated instances
"""

class Ec2_ELB_Tagging:
    def __init__(self):
        self.ec2_client       = boto3.client('ec2')
        self.ec2_resource     = boto3.resource('ec2')
        self.elb              = boto3.client('elb')
        self.instance_ids     = []
        self.elb_name         = []
        self.tags_required    = {"tagOne": "Asset", "tagTwo":"Environment"}
        self.missing_tags     = []
        self.file_path        = "/root/scripts/missing_tags.txt"

    # This function will fetch all the elb names and append to elb_bame dict

    def get_all_elb_name(self):
        print("getting all ELB names")
        response = self.elb.describe_load_balancers()
        for item in response['LoadBalancerDescriptions']:
            self.elb_name.append(item['LoadBalancerName'])
        return True

    def get_elbs_missing_tags(self):
        for item in self.elb_name:
            response = self.elb.describe_tags(LoadBalancerNames=[item])['TagDescriptions'][0]
            if len(response['Tags']) == 0:
                missing_tag = {}
                missing_tag['name'] = item
                self.missing_tags.append(missing_tag)

    def get_instance_id_for_elbs_missing_tags(self):
        for index_val in range(0, len(self.missing_tags)):
            instance_id = self.elb.describe_load_balancers(LoadBalancerNames=[self.missing_tags[index_val]['name']])['LoadBalancerDescriptions'][0]['Instances'][0]['InstanceId']
            self.missing_tags[index_val]['instance_id'] = instance_id

    def get_instance_tags_for_missing_elbs(self):
        counter = 0
        for missing_tag in self.missing_tags:
            instance = missing_tag['instance_id']
            response = self.ec2_client.describe_instances(InstanceIds=[instance])['Reservations'][0]['Instances'][0]['Tags']
            for value in response:
                if value['Key'] == "Environment":
                    self.missing_tags[counter]['Environment'] = value['Value']
                if value['Key'] == "Asset":
                    self.missing_tags[counter]['Asset'] = value['Value']
            counter += 1
        print(self.missing_tags)

    def add_tags_to_elbs(self):
        for missing_tag in self.missing_tags:
            self.elb.add_tags(LoadBalancerNames=[missing_tag['name']],
                              Tags=[{'Key': 'Environment', 'Value' : missing_tag['Environment']},
                                   {'Key': 'Asset', 'Value': missing_tag['Asset']}])

        print("Successfully added Tags to elb's")

    def main(self):
        self.get_all_elb_name()
        self.get_elbs_missing_tags()
        self.get_instance_id_for_elbs_missing_tags()
        self.get_instance_tags_for_missing_elbs()
        self.add_tags_to_elbs()


if __name__ == "__main__":
    ec2 = Ec2_ELB_Tagging()
    ec2.main()


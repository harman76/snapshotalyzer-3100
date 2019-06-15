import boto3
import botocore
import click

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

def filter_instances(project):
    instances = []
    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()
    return instances

#Added below three lines to get the commnads
@click.group()
def cli():
    """manage snapshots"""

@cli.group('instances')
def instances():
    """Commands for Instances"""
@cli.group('volumes')
def volumes():
    """Commands for Volumes"""
@cli.group('snapshots')
def snapshots():
    """Commands for Snapshots"""

@instances.command('list')
#@click.command() is commented and added @instances.command('list')
#@click.command()
@click.option('--project', default=None,
    help="Only instance for project (tag Project:<name>)")
def list_instances(project):
    "List EC2 instances"
    instances = filter_instances(project)

    for i in instances:
        tags = {t['Key']:t['Value'] for t in i.tags or [] }
        print(', '.join((i.id,
#        print(i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tags.get('Project', '<no project>'))))
    return

#LIST OF VOLUMES FROM INSTANCES
@volumes.command('list')
@click.option('--project', default=None,
    help="Only volumes for project (tag Project:<name>)")
def list_volumes(project):
    "List EC2 instances"
    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
#        tags = {t['Key']:t['Value'] for t in i.tags or [] }
            print(', '.join((v.id,
                i.id,
                v.state,
                str(v.size)  + "GiB",
                v.encrypted and "Encrypted" or "Not Encrypted"
                )))
    return

#SNAPSHOT
#LIST OF SNAPSHOT FROM INSTANCES
@snapshots.command('list')
@click.option('--all', 'list_all', default=False,is_flag=True, help="List of snapshots")
@click.option('--project', default=None,
    help="Only volumes for project (tag Project:<name>)")
def list_snapshots(project, list_all):
    "List EC2 instances"
    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(', '.join((s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c")
                )))
                if s.state == 'completed' and not list_all: break
    return
# CREATE SNAPSHOT
@instances.command('snapshot', help="Creating Sanpshot for volumes")
@click.option('--project', default=None,
    help="Only volumes for project (tag Project:<name>)")
def create_snapshots(project):
    "Create Snapshots instances"
    instances = filter_instances(project)
    for i in instances:
        print("Stopping Instances {0}...".format(i.id))
        i.stop()
        i.wait_until_stopped()
        for v in i.volumes.all():
            print("Createing Snapshots of {0}...".format(v.id) )
            v.create_snapshot(Description="Createing Snapshot")
        print("Starting Instance {0}...".format(i.id))
        i.start()
        i.wait_until_running()
    print("job Done!...")
    return


@instances.command('stop')
@click.option('--project', default=None,
    help="Only instance for project")
def stop_instances(project):
    "Stop EC2 instances"
    instances = filter_instances(project)

    for i in instances:
        print("Stopping {0}...".format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print(" Couldnot stop {0}.. ".format(i.id) + str(e))
            continue
    return

@instances.command('start')
@click.option('--project', default=None,
    help="Only instance for project")
def start_instances(project):
    "Start EC2 instances"
    instances = filter_instances(project)

    for i in instances:
        print("Starting {0}...".format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print(" Couldnot start {0}.. ".format(i.id) + str(e))
            continue
    return

if __name__ == '__main__':
#commented in 2nd section and added instances()
#instances() commented so that groups can work with cli()
#    list_instances()
#    instances()
    cli()

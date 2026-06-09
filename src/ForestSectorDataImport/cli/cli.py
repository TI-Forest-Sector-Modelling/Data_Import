import click
import ForestSectorDataImport.main as main 


@click.group()
def cli():
    """FSM Data Import CLI"""
    pass

@cli.command("update_check")
def update_check_cli():
    main.check_version_build_metadata()

#start download and formatiation for calibration input
@cli.command("calibration")
def load_data_cli():
    main.calibration_data()

@cli.command("armington")
def armington_cli():
    main.armington_data()

# cli.add_command(update_check_cli, name="timba")
# cli.add_command(load_data_cli, name="load_data")
# cli.add_command(armington_cli, name="armington_cli")

if __name__ == "__main__":
    cli()


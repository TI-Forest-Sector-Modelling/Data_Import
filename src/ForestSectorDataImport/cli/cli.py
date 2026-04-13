import click
import ForestSectorDataImport.main as main 

def cli():
    """FSM Data Import CLI"""
    pass

@cli.command("update_check")
def update_check_cli():
    main.check_version_build_metadata()

#start download and formatiation for calibration input
@click.command("calibration")
def load_data_cli():
    main.calibration_data()

# cli.add_command(update_check_cli, name="timba")
# cli.add_command(load_data_cli, name="load_data")

# if __name__ == "__main__":
#     update_check_cli()


def main():
    info('Pump Minibone after Jan diode analysis')
     
    close(description='Bone to Minibone')
    open(description='Minibone to Bone')         
    close(description='Microbone to Minibone')
    sleep(duration=1.0)
    open(description='Minibone to Turbo')
    open(description='Quad Inlet')

    set_resource(name='MinibonePumpTimeFlag',value=30)
    sleep(duration=15.0)
    close(description="Outer Pipette 1")
    close(description="Outer Pipette 2")
        
    release('JanMiniboneFlag')
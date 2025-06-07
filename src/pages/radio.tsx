import * as React from 'react';

export default function RadioPage() {
    return (
        <div className="flex flex-col items-center justify-center min-h-screen p-8">
            <h1 className="text-4xl font-bold mb-4">Internet Radio</h1>
            <p className="mb-4 text-center">Disfruta de esta muestra de transmisi\xC3\xB3n en vivo.</p>
            <audio controls autoPlay className="w-full">
                <source src="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" type="audio/mpeg" />
                Tu navegador no soporta el elemento de audio.
            </audio>
        </div>
    );
}

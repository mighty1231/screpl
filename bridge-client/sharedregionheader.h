#ifndef SHAREDREGION_H
#define SHAREDREGION_H

#pragma pack(push, 1)

#define LOGGER_LINE_SIZE 216
#define LOGGER_LINE_COUNT 500
#define APP_OUTPUT_MAXSIZE 2000
#define DISPLAYBUFFER_SIZE 4000

struct SharedRegionHeader {
    char signature[160];

    // Too much milk solution #3, busy-waiting by A
    int noteToSC;
    int noteFromSC;
    unsigned int regionSize;

    /* To SC */
    char command[300];

    /* From SC */
    int frameCount;

    // several blocks...
};

#pragma pack(pop)

#endif // SHAREDREGION_H

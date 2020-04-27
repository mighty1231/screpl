#ifndef SHAREDREGION_H
#define SHAREDREGION_H

#pragma pack(push, 1)

#define LOGGER_LINE_SIZE 216
#define LOGGER_LINE_COUNT 500

struct SharedRegion {
    char signature[160];

    // Too much milk solution #3, busy-waiting by A
    int noteToSC;
    int noteFromSC;

    /* To SC */
    char command[300];

    /* From SC */
    int frameCount;

    int app_output_sz;
    char app_output[2000];

    int log_index;
    char logger_log[LOGGER_LINE_COUNT][LOGGER_LINE_SIZE];

    int displayIndex;
    char display[13][218];
    char _unused[2];
};

#pragma pack(pop)

#endif // SHAREDREGION_H

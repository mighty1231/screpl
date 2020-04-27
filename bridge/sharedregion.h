#ifndef SHAREDREGION_H
#define SHAREDREGION_H

#pragma pack(push, 1)

struct SharedRegion {
    char signature[160];

    // Too much milk solution #3, busy-waiting by A
    int noteToSC;
    int noteFromSC;

    int frameCount;

    int displayIndex;
    char display[13][218];
    char _unused[2];

    int applog_sz;
    char applog[2000];
};

#pragma pack(pop)

#endif // SHAREDREGION_H
